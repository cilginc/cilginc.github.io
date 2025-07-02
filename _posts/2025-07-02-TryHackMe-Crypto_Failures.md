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

Hey everyone! Today, we're diving into the [Crypto Failures](https://tryhackme.com/room/cryptofailures) room on TryHackMe. This room is a fantastic example of why you should never, *ever* roll your own cryptography. Let's get our hands dirty and see what happens when good intentions meet bad implementation.

---

### Step 1: Initial Reconnaissance - The Classic Nmap Scan

First things first, let's see what we're up against. We'll set our target IP as an environment variable to make life easier, then unleash `nmap` to poke around.

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

The scan reveals two open ports: SSH on port **22** and an Apache web server on port **80**. Since we don't have any credentials, the web server is our front door. Let's go see who's home!

### Step 2: Web Enumeration - Finding the Developer's Diary

Navigating to `http://$IP` in a browser, we're greeted with a message and a cookie is set. Let's inspect the page source (Ctrl+U).

```html
<p>You are logged in as guest:**********************************************************************
<p>SSO cookie is protected with traditional military grade en<b>crypt</b>ion
<!-- TODO remember to remove .bak files-->
```

Our developer friend proudly claims "military grade encryption," which in the cybersecurity world is a bit like a magician saying, "nothing up my sleeve." It's a classic sign that something fun is about to happen!

Even better, they left us a little breadcrumb in the comments: `<!-- TODO remember to remove .bak files-->`. Well, if they insist! This is a huge hint to look for backup files. Let's fire up `gobuster` to hunt them down.

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

And just like that, `gobuster` strikes gold! We've found `index.php.bak`. This is like finding the developer's diary. Let's download it with `curl` and see what secrets it holds.

```bash
❯ curl $IP/index.php.bak > index.php.bak
```

### Step 3: Source Code Analysis - Where It All Went Wrong

Now for the fun part: let's read the PHP source code and figure out how this "military grade" encryption works.

```php
<?php
include('config.php');

function generate_cookie($user,$ENC_SECRET_KEY) {
    // A 2-character salt? Interesting choice.
    $SALT=generatesalt(2); 
    
    // The string to be "encrypted".
    $secure_cookie_string = $user.":".$_SERVER['HTTP_USER_AGENT'].":".$ENC_SECRET_KEY;

    $secure_cookie = make_secure_cookie($secure_cookie_string,$SALT);

    setcookie("secure_cookie",$secure_cookie,time()+3600,'/','',false); 
    setcookie("user","$user",time()+3600,'/','',false);
}

// A wrapper for the built-in crypt() function.
function cryptstring($what,$SALT){
    return crypt($what,$SALT);
}

// This is the heart of the "encryption" logic.
function make_secure_cookie($text,$SALT) {
    $secure_cookie='';

    // It splits the string into 8-character chunks...
    foreach ( str_split($text,8) as $el ) {
        // ...and then encrypts each chunk separately.
        $secure_cookie .= cryptstring($el,$SALT);
    }
    return($secure_cookie);
}

// A standard salt generator. Nothing too crazy here.
function generatesalt($n) {
    $randomString='';
    $characters = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
    for ($i = 0; $i < $n; $i++) {
        $index = rand(0, strlen($characters) - 1);
        $randomString .= $characters[$index];
    }
    return $randomString;
}

// This function checks if our cookie is legit.
function verify_cookie($ENC_SECRET_KEY){
    $crypted_cookie=$_COOKIE['secure_cookie'];
    $user=$_COOKIE['user'];
    $string=$user.":".$_SERVER['HTTP_USER_AGENT'].":".$ENC_SECRET_KEY;

    // It gets the salt from the first 2 characters of the cookie.
    $salt=substr($_COOKIE['secure_cookie'],0,2);

    // It re-creates the cookie and compares it to the one we sent.
    if(make_secure_cookie($string,$salt)===$crypted_cookie) {
        return true;
    } else {
        return false;
    }
}

// Main logic of the page.
if ( isset($_COOKIE['secure_cookie']) && isset($_COOKIE['user']))  {
    $user=$_COOKIE['user'];
    if (verify_cookie($ENC_SECRET_KEY)) {
        // If the cookie is valid AND the user is "admin", we get the flag!
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
} else {
    // If we don't have a cookie, it generates one for 'guest' and reloads.
    generate_cookie('guest',$ENC_SECRET_KEY);
    header('Location: /');
}
?>
```

**The Vulnerability:**

After dissecting the code, the fatal flaw becomes clear. The `make_secure_cookie` function splits the input string (`user:User-Agent:SecretKey`) into 8-character chunks and then runs each chunk through PHP's `crypt()` function.

Here's the problem: The `crypt()` function (using DES) **only considers the first 8 characters of its input string**.

This means that our developer has created a system where only the first block of the cookie matters for user authentication. The cookie is built like this:

`crypt("guest:AA", $salt)` + `crypt(":some_se", $salt)` + `crypt("cret_key", $salt)` + ...

The `verify_cookie` function checks the username from a separate `user` cookie. If we set `user=admin`, the server will try to validate a string starting with `admin:`. Our goal is to create a valid cookie for the string `admin:AA...`.

Since `crypt()` only cares about the first 8 characters, we only need to forge the *first* block of the cookie! We can take a valid guest cookie, replace its first encrypted block with one we generate for `admin:AA`, and leave the rest of the cookie untouched. The server will happily accept it!

### Step 4: Exploitation, Part 1 - Forging an Admin Cookie

Now that we have a plan, let's write a Python script to do the dirty work.

```python
import requests
import sys

# The 'crypt' module is a must-have for this. It's not available on Windows, sorry!
try:
    import crypt
except ImportError:
    print("Bummer, the 'crypt' module isn't on your system. This script won't work on Windows.")
    sys.exit(1)

# --- Point it at the target ---
IP = "10.10.183.237"
URL = f"http://{IP}/"
USER_AGENT = "AA" # A short, simple User-Agent to make our lives easier

print("Alright, let's work some magic and become admin.")

# 1. Get a legitimate guest cookie to use as our template
print(">> Knocking on the door as 'guest' to grab a cookie...")
s = requests.Session()
s.headers.update({'User-Agent': USER_AGENT})
res = s.get(URL, allow_redirects=False)
guest_cookie = s.cookies.get('secure_cookie')

if not guest_cookie:
    print("!! Houston, we have a problem. Didn't get a cookie. Is the server up?")
    sys.exit(1)

# 2. Extract the salt and the rest of the cookie we want to keep
salt = guest_cookie[:2] # The first 2 characters are the salt
cookie_tail = guest_cookie[13:] # The rest of the cookie, which we'll reuse
print(f">> Got the salt: '{salt}'. Now to forge the admin part.")

# 3. Create our forged first block.
# The original block was for "guest:AA". We'll make one for "admin:AA".
# Both are 8 characters, so crypt() will treat them similarly.
admin_first_chunk = "admin:" + USER_AGENT
admin_first_block = crypt.crypt(admin_first_chunk, salt)
forged_cookie = admin_first_block + cookie_tail

# 4. Send the forged cookie and claim our prize!
print(">> Sending the forged cookie... Fingers crossed!")
cookies = {'user': 'admin', 'secure_cookie': forged_cookie}
res = requests.get(URL, headers={'User-Agent': USER_AGENT}, cookies=cookies)

print("\n----------------- SERVER RESPONSE -----------------")
print(res.text.strip())
print("---------------------------------------------------")
```

Running this script gives us the first flag! But the server taunts us: "Now I want the key." Challenge accepted.

### Step 5: Exploitation, Part 2 - Cracking the Secret Key

To get the secret key, we have to reverse-engineer the cookie. We know the cookie is made of encrypted 8-character chunks of the key. We can take a valid cookie, isolate each chunk, and brute-force the plaintext that generates it.

Let's get a script running.

```python
import requests
import sys
import string
from urllib.parse import unquote

# The 'crypt' module is needed, but it's not on Windows.
try:
    import crypt
except ImportError:
    print("Bummer, the 'crypt' module isn't on your system. This script won't work on Windows.")
    sys.exit(1)

# --- Point it at the target ---
IP = "10.10.183.237"
URL = f"http://{IP}/"

# We'll use all printable characters for the brute-force.
CHARSET = string.printable

def find_key():
    """
    Finds the secret key one character at a time using a block alignment oracle.
    """
    found_key = ""
    print("Alright, let's find that secret key. This might take a minute.\n")

    while True:
        # We'll try to find the next character in the key.
        next_char_num = len(found_key) + 1
        print(f"[*] Searching for character #{next_char_num}...")

        # 1. Align the block
        # We adjust the User-Agent padding until our target character is the
        # last byte of an 8-byte block.
        for pad_length in range(1, 9):
            user_agent = 'x' * pad_length
            
            # This is the string we're building. '*' is the placeholder for the char we want.
            plaintext_to_align = f"guest:{user_agent}:{found_key}*"
            
            if len(plaintext_to_align) % 8 == 0:
                # Perfect alignment! The '*' is at the end of a block.
                # The 7 characters before it are our known prefix.
                block_prefix = plaintext_to_align[-8:-1]
                break
        
        # 2. Brute-force the aligned character
        # Get a fresh cookie from the server using the correct padding.
        try:
            res = requests.get(URL, headers={'User-Agent': user_agent}, allow_redirects=False, timeout=5)
            real_cookie = unquote(res.cookies['secure_cookie'])
            salt = real_cookie[:2]
        except (requests.RequestException, KeyError) as e:
            print(f"\n[!] Failed to get a cookie from the server: {e}")
            return None
            
        found_next_char = False
        for char_guess in CHARSET:
            # Build the full 8-byte block we're testing.
            test_block = block_prefix + char_guess
            
            # Encrypt it and see if it's in the real cookie.
            hashed_block = crypt.crypt(test_block, salt)
            
            if hashed_block in real_cookie:
                # We found it!
                found_key += char_guess
                found_next_char = True
                # Print progress on the same line.
                print(f"\r[+] Key found so far: {found_key}", end="", flush=True)
                break # Move on to find the *next* character.
        
        print() # Move to the next line for the next character search.

        if not found_next_char:
            # If we went through all characters and found nothing, we must be at the end of the key.
            print("[*] No more characters found. Assuming the key is complete.")
            break
            
    return found_key

if __name__ == "__main__":
    key = find_key()

    if key:
        print("\n=======================================")
        print(f"  Jackpot! The secret key is:")
        print(f"  {key}")
        print("=======================================")
```

Fire up the script, grab a coffee (or two), and let the computer do the heavy lifting. This process brute-forces each 13-character segment of the cookie to find its 8-character plaintext source. After a short wait, it will piece together the secret key, and the room is complete!

**Key Takeaway:** This room is a perfect illustration of the #1 rule of cryptography: **Don't roll your own crypto!** Use well-vetted, standard libraries and understand how they work under the hood. A simple misunderstanding of a function like `crypt()` can unravel your entire security model.

Happy hacking
