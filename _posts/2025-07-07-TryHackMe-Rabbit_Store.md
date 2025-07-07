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
