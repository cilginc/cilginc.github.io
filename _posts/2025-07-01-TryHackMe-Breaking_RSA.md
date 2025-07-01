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

Hi I'm making room <https://tryhackme.com/room/breakrsa>

---

```bash
export IP=10.10.243.171
```


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

```bash
❯ curl $IP                 
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
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

Lets try fuzzing the webserver using `gobuster`.



```bash
❯ gobuster dir -w common.txt -u http://$IP -x md,js,html,php,py,css,txt -t 50 
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

And we found the secret directory. In this directory there is 2 two files
1. rsa public key
2. some log file saying:

```text
The library we are using to generate SSH keys implements RSA poorly. The two
randomly selected prime numbers (p and q) are very close to one another. Such
bad keys can easily be broken with Fermat's factorization method.

Also, SSH root login is enabled.

<https://github.com/murtaza-u/zet/tree/main/20220808171808>

---
```

