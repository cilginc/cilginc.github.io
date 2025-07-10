---
title: "TryHackMe: WhyHackMe"
author: cilgin
date: 2025-07-10 13:56:25 +0300
categories: [CyberSecurity]
tags: [CTF, TryHackMe, Medium]
pin: false
math: false
mermaid: false
image:
  path: /assets/img/2025-07-10-TryHackMe-WhyHackMe/main.webp
---

Hi I'm making [TryHackMe WhyHackMe](https://tryhackme.com/room/whyhackme) room.

---

```bash
IP=10.10.168.55
```

```bash
❯ nmap -T4 -n -sC -sV -Pn -p- $IP
Starting Nmap 7.97 ( https://nmap.org ) at 2025-07-10 14:00 +0300
Nmap scan report for 10.10.168.55
Host is up (0.070s latency).
Not shown: 65531 closed tcp ports (conn-refused)
PORT      STATE    SERVICE VERSION
21/tcp    open     ftp     vsftpd 3.0.3
| ftp-syst:
|   STAT:
| FTP server status:
|      Connected to 10.21.206.128
|      Logged in as ftp
|      TYPE: ASCII
|      No session bandwidth limit
|      Session timeout in seconds is 300
|      Control connection is plain text
|      Data connections will be plain text
|      At session startup, client count was 3
|      vsFTPd 3.0.3 - secure, fast, stable
|_End of status
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
|_-rw-r--r--    1 0        0             318 Mar 14  2023 update.txt
22/tcp    open     ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.9 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   3072 47:71:2b:90:7d:89:b8:e9:b4:6a:76:c1:50:49:43:cf (RSA)
|   256 cb:29:97:dc:fd:85:d9:ea:f8:84:98:0b:66:10:5e:6f (ECDSA)
|_  256 12:3f:38:92:a7:ba:7f:da:a7:18:4f:0d:ff:56:c1:1f (ED25519)
80/tcp    open     http    Apache httpd 2.4.41 ((Ubuntu))
|_http-title: Welcome!!
|_http-server-header: Apache/2.4.41 (Ubuntu)
41312/tcp filtered unknown
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 65.77 seconds
```

Lets firstly go to the website.

![Desktop View](/assets/img/2025-07-10-TryHackMe-WhyHackMe/photo1.webp){: width="972" height="589" }

Looks like very simple php website.

Looking throught website I found some login endpotint `/login.php`

![Desktop View](/assets/img/2025-07-10-TryHackMe-WhyHackMe/photo2.webp){: width="972" height="589" }

admin admin didn't worked lets firstly fuzz the website using `gobuster`.

```bash
❯ gobuster dir -w common.txt -u http://$IP/ -x md,js,html,php,py,css,txt,bak -t 50
===============================================================
Gobuster v3.7
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://10.10.168.55/
[+] Method:                  GET
[+] Threads:                 50
[+] Wordlist:                common.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.7
[+] Extensions:              py,css,txt,bak,md,js,html,php
[+] Timeout:                 10s
===============================================================
Starting gobuster in directory enumeration mode
===============================================================
/assets               (Status: 301) [Size: 313] [--> http://10.10.168.55/assets/]
/blog.php             (Status: 200) [Size: 3102]
/cgi-bin/             (Status: 403) [Size: 277]
/config.php           (Status: 200) [Size: 0]
/dir                  (Status: 403) [Size: 277]
/index.php            (Status: 200) [Size: 563]
/login.php            (Status: 200) [Size: 523]
/logout.php           (Status: 302) [Size: 0] [--> login.php]
/register.php         (Status: 200) [Size: 643]
/server-status        (Status: 403) [Size: 277]
Progress: 42651 / 42651 (100.00%)
===============================================================
Finished
===============================================================
```

And I found register.php so lets register a account first and try to log in.

![Desktop View](/assets/img/2025-07-10-TryHackMe-WhyHackMe/photo3.webp){: width="972" height="589" }

I logged in but thats it i think.

It says that now we can comment on posts.

Maybe we can try to exploit that.

Firstly lets log in Anonymous on ftp.

```bash
root@e3769c930fc5:/data# ftp 10.10.168.55 21
Connected to 10.10.168.55.
220 (vsFTPd 3.0.3)
Name (10.10.168.55:root): anonymous
331 Please specify the password.
Password:
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
ftp> ls
229 Entering Extended Passive Mode (|||53253|)
150 Here comes the directory listing.
-rw-r--r--    1 0        0             318 Mar 14  2023 update.txt
226 Directory send OK.
ftp> ls -la
229 Entering Extended Passive Mode (|||5144|)
150 Here comes the directory listing.
drwxr-xr-x    2 0        119          4096 Mar 14  2023 .
drwxr-xr-x    2 0        119          4096 Mar 14  2023 ..
-rw-r--r--    1 0        0             318 Mar 14  2023 update.txt
226 Directory send OK.
```

Lets download update.txt

```bash
ftp> get update.txt
```

```bash
❯ cat update.txt
Hey I just removed the old user mike because that account was compromised and for any of you who wants the creds of new account visit 127.0.0.1/dir/pass.txt and don't worry this file is only accessible by localhost(127.0.0.1), so nobody else can view it except me or people with access to the common account.
- admin
```
