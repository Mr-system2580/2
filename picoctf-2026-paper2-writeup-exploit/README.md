# picoctf-paper2-solution
Hardest Challenge in PicoCTF 2026 solution
# picoCTF `paper-2` Writeup

## Challenge Information

**Name:** `paper-2`  
**Category:** Web Exploitation  
**Points:** 500  
**Author:** ehhthing

## Description

> A piece of paper is a blank canvas, what do you want on yours?

We are given a web challenge that lets us upload content and have a bot visit it. The challenge also contains a hidden secret, and once we recover that secret, we can request the real flag.

The intended solve path is:

1. Understand how uploaded files are rendered.
2. Abuse the bot’s browser context.
3. Leak the secret.
4. Send the secret to the flag endpoint.
5. Get the final `picoCTF{...}` flag.

---

## Final Flag

```text
picoCTF{i_l1ke_frames_on_my_canvas_953d5fff}
Solver Usage

The exploit script is run like this:

python3 solve.py <instance>

Example:

python3 solve.py https://lonely-island.picoctf.net:59702

Successful output:

[+] webhook token: 8099f28f-9c3f-430f-a7c0-316226495ccd
[+] callback URL: https://webhook.site/8099f28f-9c3f-430f-a7c0-316226495ccd
[+] uploaded stage 2 PDF as /paper/1
[+] uploaded stage 1 XML as /paper/2
[+] bot triggered
[+] leaked URL: https://web/paper/1#653c1663007b0df4dbf1abcbefb19fff
[+] secret: 653c1663007b0df4dbf1abcbefb19fff
[+] flag: picoCTF{i_l1ke_frames_on_my_canvas_953d5fff}
Overview

This challenge is a browser exploitation challenge built around a bot that opens attacker-controlled uploaded content.

At a high level, the exploit works by chaining two uploaded files:

a Stage 1 XML
a Stage 2 PDF

The bot first visits the XML file. That file causes the browser to load the malicious PDF. The PDF then triggers behavior that leaks the challenge secret through a webhook. After that, the script extracts the secret and uses it to request the real flag.

So the challenge is not a simple reflected XSS or classic HTML injection. It is more about:

attacker-controlled file rendering
browser behavior differences between formats
bot interaction
exfiltration using a side channel
Key Idea

The challenge tries to restrict direct script-based attacks, but browser file renderers are not all equal.

A normal HTML page may be tightly restricted by CSP or sanitization. But once a browser opens other file types like XML or PDF, different parsing and rendering paths may come into play.

That difference is what makes the exploit possible.

The solver uses:

an XML file to get the bot into the right browsing flow
a PDF file to trigger the leak
a webhook to receive the leaked data
the leaked secret to retrieve the flag
What Makes This Vulnerable?
1. The bot opens attacker-controlled files

This is the core risk. The app allows us to upload content and then asks a privileged browser bot to visit it.

Any time a challenge lets users do both of these things together, there is a strong chance of exploitation:

upload content
get a bot to load it
abuse differences in file handling or browser features

If the bot has access to protected pages or internal state, attacker-controlled rendering becomes dangerous.

2. Uploaded files are not all equally safe

A common mistake in web challenges is assuming that if HTML is sanitized or restricted, other formats are harmless.

That is not true.

Browsers can treat files differently depending on type:

HTML
SVG
XML
PDF

Even when direct JavaScript is blocked in one context, a different file type may still give a useful primitive. In this challenge, the important file type is PDF.

3. The secret can be leaked indirectly

The exploit does not need to directly read the secret from the page DOM in the usual way.

Instead, it makes the browser navigate in a way that places the secret into a URL fragment like this:

https://web/paper/1#653c1663007b0df4dbf1abcbefb19fff

The part after # is the leaked secret:

653c1663007b0df4dbf1abcbefb19fff

Once the browser reaches a state where the secret is embedded into a controllable URL, the solver can exfiltrate it using a webhook.

Exploit Strategy

The solve script follows a clear multi-stage plan.

Stage 0: Set up an out-of-band receiver

The first thing the script does is prepare a webhook callback.

This gives the exploit somewhere to send data after the browser leak succeeds.

That is why the script prints:

[+] webhook token: ...
[+] callback URL: ...

Without this step, we would have no reliable way to collect the leaked secret.

Stage 1: Upload the malicious PDF

The PDF is the second-stage payload, but it must usually be uploaded first so the first-stage file can reference it.

The script uploads the PDF and receives a path like:

/paper/1

Output:

[+] uploaded stage 2 PDF as /paper/1

This PDF is the important exploitation payload. It is what eventually causes the secret to leak.

Stage 2: Upload the malicious XML

Next, the script uploads an XML file.

Output:

[+] uploaded stage 1 XML as /paper/2

This XML acts as a launcher or bridge into the second stage. It is the file the bot visits first.

The XML causes the browser to load the malicious PDF under attacker-controlled conditions.

Stage 3: Trigger the bot

Once both files are uploaded, the solver tells the challenge bot to visit the XML stage.

Output:

[+] bot triggered

This is where the real attack happens.

The bot loads the XML, which leads into the PDF, and the PDF triggers the leak chain.

Stage 4: Receive the leaked secret

After the bot runs the chain successfully, the secret is leaked to the webhook.

The script reads the webhook activity and extracts the important value from the leaked URL.

Observed output:

[+] leaked URL: https://web/paper/1#653c1663007b0df4dbf1abcbefb19fff
[+] secret: 653c1663007b0df4dbf1abcbefb19fff

This tells us the exploit worked.

The secret is the hex value after #.

Stage 5: Request the flag

Once the secret is known, the rest is simple.

The script sends the secret back to the challenge’s flag endpoint.

Output:

[+] flag: picoCTF{i_l1ke_frames_on_my_canvas_953d5fff}

That is the final flag.

Full Attack Chain

Here is the complete flow in order:

Create a unique webhook callback.
Generate a malicious PDF.
Generate a malicious XML that leads to the PDF.
Upload the PDF.
Upload the XML.
Ask the bot to visit the XML.
The bot loads the XML.
The XML causes the browser to open the PDF.
The PDF triggers a browser action that leaks the secret into a URL fragment.
The leaked value is received through the webhook.
Parse the secret.
Send the secret to the flag endpoint.
Print the flag.
Step-by-Step Explanation of the Solver

Below is the logic of solve.py explained in a way that matches how the exploit works.

1. Read the instance URL

The script expects the current challenge instance as a command-line argument:

base = sys.argv[1].rstrip("/")

This makes the solver reusable, because picoCTF instances often change ports each time they are launched.

Example:

python3 solve.py https://lonely-island.picoctf.net:59702
2. Create a webhook token

The solver needs a place to receive exfiltrated data.

So it creates or uses a webhook token, then builds a callback URL:

token = create_webhook_token()
callback_url = f"https://webhook.site/{token}"

This URL will later receive the leaked request from the bot.

The script prints:

[+] webhook token: ...
[+] callback URL: ...
3. Build the PDF payload

The script generates a malicious PDF as the second stage.

This is the most important part of the exploit chain.

The exact PDF internals can vary depending on how the script was written, but conceptually the PDF is crafted so that when it is opened by the bot’s browser, it causes navigation or execution behavior that results in a URL like:

https://web/paper/1#<secret>

That is the leak primitive.

The important point is that the PDF is not just treated as a passive document. It is being used as an active browser exploitation payload.

4. Build the XML payload

The script also generates an XML file for stage 1.

This XML is the file that the bot is told to visit first.

Its job is to transition the bot into the second stage, usually by causing the browser to fetch or render the uploaded PDF.

So the XML is not the final exploit by itself. It is the delivery mechanism for the PDF stage.

5. Upload both files

The solver uploads the PDF first, then uploads the XML.

This order matters because the XML stage often needs to reference the PDF’s uploaded location.

That is why the output looks like:

[+] uploaded stage 2 PDF as /paper/1
[+] uploaded stage 1 XML as /paper/2

The XML knows where to find the already-uploaded PDF.

6. Trigger the bot visit

Once the payload chain is in place, the script triggers the challenge bot.

Conceptually it is something like:

requests.get(f"{base}/visit/{xml_id}")

or an equivalent route used by the app.

From that point on, the browser executes the chain for us.

7. Poll the webhook for incoming requests

Now the solver waits for evidence that the bot has reached the exfiltration stage.

It repeatedly polls the webhook logs until it sees the leaked URL.

Conceptually:

while True:
    logs = get_webhook_requests(token)
    if found_secret(logs):
        break

This is a common pattern in CTF browser challenges:

trigger the bot
wait for the callback
parse the leaked data
8. Parse the secret

Once the webhook logs show a URL like:

https://web/paper/1#653c1663007b0df4dbf1abcbefb19fff

the script extracts:

653c1663007b0df4dbf1abcbefb19fff

That is the secret required by the server.

9. Request the flag

The last step is to submit the secret to the challenge’s flag route.

Conceptually:

requests.get(f"{base}/flag", params={"secret": secret})

The server verifies the secret, and if it matches, it returns the real flag.

That produces:

picoCTF{i_l1ke_frames_on_my_canvas_953d5fff}
Why the Exploit Works

This challenge is interesting because it is not simply “inject <script> and win.”

Instead, the exploit works because of a combination of design weaknesses:

Untrusted file rendering

The app lets us upload files that the browser later renders.

Bot trust

The bot will load attacker-controlled content.

File-type-specific browser behavior

The PDF renderer behaves differently from ordinary HTML pages.

Indirect data leakage

Even without direct DOM access, the browser can still be tricked into putting the secret in a controlled location.

Out-of-band collection

The webhook gives us a place to receive the leak.

That combination is what makes the exploit possible.

Why XML and PDF?

This is one of the most educational parts of the challenge.

The reason two stages are used is that a single file often is not enough to produce the exact browsing conditions needed.

The XML stage helps guide the browser into the PDF stage.

Then the PDF stage uses browser behavior that is different from a normal HTML page, allowing the attacker to reach a primitive that survives the challenge’s defenses.

So the chain is:

XML for delivery
PDF for exploitation
webhook for exfiltration

That is a very CTF-style browser exploit chain.

Observed Secret and Flag

From the successful run:

Secret
653c1663007b0df4dbf1abcbefb19fff
Flag
picoCTF{i_l1ke_frames_on_my_canvas_953d5fff}
Example Full Run
cd /tmp
python3 solve.py https://lonely-island.picoctf.net:59702
