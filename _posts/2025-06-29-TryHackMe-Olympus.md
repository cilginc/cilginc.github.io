---
title: "TryHackMe: Olympus"
author: cilgin
date: 2025-06-29 19:51:50 +0300
categories: [CyberSecurity]
tags: [CTF, TryHackMe, Medium]
pin: true
math: false
mermaid: false
image:
  path: /assets/img/2025-06-29-TryHackMe-Olympus/main.png
---

Hi

---

```bash
export IP=10.10.85.12
```

typical nmap scan

```bash
❯ nmap -A -p- $IP
Starting Nmap 7.97 ( https://nmap.org ) at 2025-06-29 20:08 +0300
Nmap scan report for olympus.thm (10.10.85.12)
Host is up (0.066s latency).
Not shown: 65533 closed tcp ports (conn-refused)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.13 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   3072 fa:d5:56:cd:de:f2:25:02:3f:ac:8f:1f:13:93:87:da (RSA)
|   256 8e:79:67:bf:ba:b3:01:9a:47:00:ca:c1:28:8c:79:7a (ECDSA)
|_  256 a1:ae:62:c2:24:94:4d:d3:b6:c8:30:87:76:a6:10:fe (ED25519)
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
|_http-server-header: Apache/2.4.41 (Ubuntu)
|_http-title: Olympus
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 611.24 seconds
```

In browster I go to the website and redirected to olympus.thm
Add the ip address to the /etc/hosts

![Desktop View](/assets/img/2025-06-29-TryHackMe-Olympus/photo1.png){: width="972" height="589" }

We can see that site is under development. And saying old version of this site is under this domain.
So we can fuzz all the subdomains for this domain.

Fuzzing time using `gobuster`

I fuzzed all the subdomains using gobuster but found nothing so after that i tried fuzzing directories.

```bash
❯ gobuster dir -w common.txt -u http://olympus.thm/ -x md,js,html,php,py,css,txt -t 50
===============================================================
Gobuster v3.6
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://olympus.thm/
[+] Method:                  GET
[+] Threads:                 50
[+] Wordlist:                common.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.6
[+] Extensions:              py,css,txt,md,js,html,php
[+] Timeout:                 10s
===============================================================
Starting gobuster in directory enumeration mode
===============================================================
/index.php            (Status: 200) [Size: 1948]
/index.php            (Status: 200) [Size: 1948]
/javascript           (Status: 301) [Size: 315] [--> http://olympus.thm/javascript/]
/phpmyadmin           (Status: 403) [Size: 276]
/server-status        (Status: 403) [Size: 276]
/static               (Status: 301) [Size: 311] [--> http://olympus.thm/static/]
/~webmaster           (Status: 301) [Size: 315] [--> http://olympus.thm/~webmaster/]

===============================================================
Finished
===============================================================
```

We can see that there is a phpmyadmin is existed.
Maybe we can later try to get into that.

And finded ~webmaster which contains the old site.

After that I fuzzde the old site:

```bash
❯ gobuster dir -w common.txt -u http://olympus.thm/~webmaster/ -x md,js,html,php,py,css,txt -t 50
===============================================================
Gobuster v3.6
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://olympus.thm/~webmaster/
[+] Method:                  GET
[+] Threads:                 50
[+] Wordlist:                common.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.6
[+] Extensions:              py,css,txt,md,js,html,php
[+] Timeout:                 10s
===============================================================
Starting gobuster in directory enumeration mode
===============================================================
/LICENSE              (Status: 200) [Size: 1070]
/README.md            (Status: 200) [Size: 2146]
/admin                (Status: 301) [Size: 321] [--> http://olympus.thm/~webmaster/admin/]
/category.php         (Status: 200) [Size: 6650]
/css                  (Status: 301) [Size: 319] [--> http://olympus.thm/~webmaster/css/]
/fonts                (Status: 301) [Size: 321] [--> http://olympus.thm/~webmaster/fonts/]
/img                  (Status: 301) [Size: 319] [--> http://olympus.thm/~webmaster/img/]
/includes             (Status: 301) [Size: 324] [--> http://olympus.thm/~webmaster/includes/]
/index.php            (Status: 200) [Size: 9386]
/index.php            (Status: 200) [Size: 9386]
/js                   (Status: 301) [Size: 318] [--> http://olympus.thm/~webmaster/js/]
/search.php           (Status: 200) [Size: 6621]
Progress: 37912 / 37912 (100.00%)
===============================================================
Finished
===============================================================
```

There is admin panel maybe i can fuzz that.

Also there is search.php maybe i can use that file to make sql injection.
