---
title: "TryHackMe: Rabbit Store"
author: cilgin
date: 2025-07-07 14:23:56 +0300
categories: [CyberSecurity]
tags: [CTF, TryHackMe, Medium]
pin: false
math: false
mermaid: false
image:
  path: /assets/img/2025-07-07-TryHackMe-Rabbit_Store/main.webp
---

Hi I'm making TryHackMe <https://tryhackme.com/room/rabbitstore> room.


---


```bash
export IP=10.10.144.3
```


```bash
❯ nmap -T4 -n -sC -sV -Pn -p- $IP
Starting Nmap 7.97 ( https://nmap.org ) at 2025-07-07 14:24 +0300
Nmap scan report for 10.10.144.3
Host is up (0.073s latency).
Not shown: 65531 closed tcp ports (conn-refused)
PORT      STATE SERVICE VERSION
22/tcp    open  ssh     OpenSSH 8.9p1 Ubuntu 3ubuntu0.10 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 3f:da:55:0b:b3:a9:3b:09:5f:b1:db:53:5e:0b:ef:e2 (ECDSA)
|_  256 b7:d3:2e:a7:08:91:66:6b:30:d2:0c:f7:90:cf:9a:f4 (ED25519)
80/tcp    open  http    Apache httpd 2.4.52
|_http-server-header: Apache/2.4.52 (Ubuntu)
|_http-title: Did not follow redirect to http://cloudsite.thm/
4369/tcp  open  epmd    Erlang Port Mapper Daemon
25672/tcp open  unknown
Service Info: Host: 127.0.1.1; OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 187.62 seconds
```


```bash
❯ curl $IP                      
<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><head>
<title>302 Found</title>
</head><body>
<h1>Found</h1>
<p>The document has moved <a href="http://cloudsite.thm/">here</a>.</p>
<hr>
<address>Apache/2.4.52 (Ubuntu) Server at 10.10.144.3 Port 80</address>
</body></html>
```

Lets add `cloudsite.thm` to `/etc/hosts`



![Desktop View](/assets/img/2025-07-07-TryHackMe-Rabbit_Store/photo1.webp){: width="972" height="589" }

You can see that this is a site cloud Saas website template


If you try to click log in you'll directed to `storage.cloudsite.thm`.


Lets try adding this to our `/etc/hosts`



![Desktop View](/assets/img/2025-07-07-TryHackMe-Rabbit_Store/photo2.webp){: width="972" height="589" }




I tried admin admin but It wanted me a e mail lets look at the site for any emails.


```text
info@smarteyeapps.com
sales@smarteyeapps.com
```

I found this too maybe it can be helpful.


The login request is like this


```text
{"email":"pwned@pwned.com","password":"123123123"}
```

on `http://storage.cloudsite.thm/api/login` end


I also created a account named pwned@pwned.com password 1234


When I log in I see this.

![Desktop View](/assets/img/2025-07-07-TryHackMe-Rabbit_Store/photo3.webp){: width="972" height="589" }


Which means we can't do anything with this account.


We can brute force found emails but firstly fuzz the website using `gobuster`



```bash
❯ gobuster dir -w common.txt -u http://cloudsite.thm -x md,js,html,php,py,css,txt,bak -t 50
===============================================================
Gobuster v3.7
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://cloudsite.thm
[+] Method:                  GET
[+] Threads:                 30
[+] Wordlist:                common.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.7
[+] Extensions:              css,txt,bak,md,js,html,php,py
[+] Timeout:                 10s
===============================================================
Starting gobuster in directory enumeration mode
===============================================================
/about_us.html        (Status: 200) [Size: 9992]
/assets               (Status: 301) [Size: 315] [--> http://cloudsite.thm/assets/]
/blog.html            (Status: 200) [Size: 10939]
/contact_us.html      (Status: 200) [Size: 9914]
/index.html           (Status: 200) [Size: 18451]
/index.html           (Status: 200) [Size: 18451]
/javascript           (Status: 301) [Size: 319] [--> http://cloudsite.thm/javascript/]
/server-status        (Status: 403) [Size: 278]
/services.html        (Status: 200) [Size: 9358]
Progress: 42651 / 42651 (100.00%)
===============================================================
Finished
===============================================================
```



```bash
❯ gobuster dir -w common.txt -u http://storage.cloudsite.thm -x md,js,html,php,py,css,txt,bak -t 50
===============================================================
Gobuster v3.7
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://storage.cloudsite.thm
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
/assets               (Status: 301) [Size: 331] [--> http://storage.cloudsite.thm/assets/]
/css                  (Status: 301) [Size: 328] [--> http://storage.cloudsite.thm/css/]
/fonts                (Status: 301) [Size: 330] [--> http://storage.cloudsite.thm/fonts/]
/images               (Status: 301) [Size: 331] [--> http://storage.cloudsite.thm/images/]
/index.html           (Status: 200) [Size: 9039]
/index.html           (Status: 200) [Size: 9039]
/javascript           (Status: 301) [Size: 335] [--> http://storage.cloudsite.thm/javascript/]
/js                   (Status: 301) [Size: 327] [--> http://storage.cloudsite.thm/js/]
/register.html        (Status: 200) [Size: 9043]
/server-status        (Status: 403) [Size: 286]
Progress: 42651 / 42651 (100.00%)
===============================================================
Finished
===============================================================
```



I found on the assets config-scss.bat

Which is a bat file.


```text
cd E:\smarteye\consulting\3\html\assets
sass --watch scss/style.scss:css/style.css
```

This could be useful maybe.



Now lets fuzz api endpoint.


```bash
❯ gobuster dir -w common.txt -u http://storage.cloudsite.thm/api/ -x md,js,html,php,py,css,txt,bak -t 50
===============================================================
Gobuster v3.7
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://storage.cloudsite.thm/api/
[+] Method:                  GET
[+] Threads:                 50
[+] Wordlist:                common.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.7
[+] Extensions:              bak,md,js,html,php,py,css,txt
[+] Timeout:                 10s
===============================================================
Starting gobuster in directory enumeration mode
===============================================================
/Login                (Status: 405) [Size: 36]
/docs                 (Status: 403) [Size: 27]
/login                (Status: 405) [Size: 36]
/register             (Status: 405) [Size: 36]
/updates-topic        (Status: 502) [Size: 428]
/uploads              (Status: 401) [Size: 32]
Progress: 42651 / 42651 (100.00%)
===============================================================
Finished
===============================================================
```
I don't know what but there are two login endpoint `Login` and `login`

Maybe Login one could be vulnerable


I don't know what but i nuked my previus acocunt whatever make new one.


After trying /api/docs I found something:



```bash
❯ curl -s http://storage.cloudsite.thm/api/uploads
{"message":"Token not provided"}%                                                                       
```

If we go to the browser I get:

```text
message	"Your subscription is inactive. You cannot use our services."
```

```bash
❯ curl -s 'http://storage.cloudsite.thm/api/uploads' -H 'Cookie: jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImFAYS5jb20iLCJzdWJzY3JpcHRpb24iOiJpbmFjdGl2ZSIsImlhdCI6MTc1MTg4OTkyMywiZXhwIjoxNzUxODkzNTIzfQ.qQb3z00lku8yAT6qCmXzKfugOoiJhbYV54va3Fmc07w'
{"message":"Your subscription is inactive. You cannot use our services."}%     
```

So maybe there is a thing in the token lets decode the token first.

After jwt decode I get this.

```text
{
    "email": "a@a.com",
    "subscription": "inactive",
    "iat": 1751889923,
    "exp": 1751893523
}
```
