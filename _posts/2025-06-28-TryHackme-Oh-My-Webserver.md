---
title: "TryHackMe: Oh My Webserver"
author: cilgin
date: 2025-06-28 14:10:53 +0300
categories: [CyberSecurity]
tags: [CTF, TryHackMe, Easy]
pin: true
math: false
mermaid: false
image:
  path: /assets/img/2025-06-28-TryHackme-Oh-My-Webserver/main.png
---

Hi

---


```bash
export IP=10.10.185.160
```


```bash
❯ nmap -T4 -n -sC -sV -Pn -p- $IP
Starting Nmap 7.97 ( https://nmap.org ) at 2025-06-28 14:12 +0300
Nmap scan report for 10.10.109.2
Host is up (0.071s latency).
Not shown: 65533 filtered tcp ports (no-response)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.13 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 d9:ed:8e:b8:88:73:3b:93:8e:05:7b:2d:08:1e:86:f6 (RSA)
|   256 6b:8a:62:60:44:4a:b5:5a:bc:16:90:b7:66:69:cb:48 (ECDSA)
|_  256 d9:31:27:bf:cb:d2:a1:3e:63:6e:75:ee:61:76:52:73 (ED25519)
80/tcp open  http    Apache httpd 2.4.49 ((Unix))
| http-methods: 
|_  Potentially risky methods: TRACE
|_http-title: Consult - Business Consultancy Agency Template | Home
|_http-server-header: Apache/2.4.49 (Unix)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 166.55 seconds
```


I go the website and look to the source code. At the and I see this code:

```html
    <!--====== Jquery js ======-->
    <script src="assets/js/vendor/jquery-1.12.4.min.js"></script>
    <script src="assets/js/vendor/modernizr-3.7.1.min.js"></script>
    
    <!--====== Bootstrap js ======-->
    <script src="assets/js/popper.min.js"></script>
    <script src="assets/js/bootstrap.min.js"></script>
    
    <!--====== Slick js ======-->
    <script src="assets/js/slick.min.js"></script>
    
    <!--====== Isotope js ======-->
    <script src="assets/js/imagesloaded.pkgd.min.js"></script>
    <script src="assets/js/isotope.pkgd.min.js"></script>
    
    <!--====== Counter Up js ======-->
    <script src="assets/js/waypoints.min.js"></script>
    <script src="assets/js/jquery.counterup.min.js"></script>
    
    <!--====== Circles js ======-->
    <script src="assets/js/circles.min.js"></script>
    
    <!--====== Appear js ======-->
    <script src="assets/js/jquery.appear.min.js"></script>
    
    <!--====== WOW js ======-->
    <script src="assets/js/wow.min.js"></script>
    
    <!--====== Headroom js ======-->
    <script src="assets/js/headroom.min.js"></script>
    
    <!--====== Jquery Nav js ======-->
    <script src="assets/js/jquery.nav.js"></script>
    
    <!--====== Scroll It js ======-->
    <script src="assets/js/scrollIt.min.js"></script>
    
    <!--====== Magnific Popup js ======-->
    <script src="assets/js/jquery.magnific-popup.min.js"></script>
    
    <!--====== Main js ======-->
    <script src="assets/js/main.js"></script>
```

Maybe I can use this.


But firstly I run gobuster:
```bash
❯ gobuster dir -w common.txt -u http://$IP -x md,js,html,php,py,css,txt -t 50
===============================================================
Gobuster v3.6
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://10.10.109.2
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
/assets               (Status: 301) [Size: 234] [--> http://10.10.109.2/assets/]
/cgi-bin/             (Status: 403) [Size: 199]
/cgi-bin/.html        (Status: 403) [Size: 199]
/index.html           (Status: 200) [Size: 57985]
/index.html           (Status: 200) [Size: 57985]
Progress: 37912 / 37912 (100.00%)
===============================================================
Finished
===============================================================
```

```bash
❯ gobuster dir -w common.txt -u http://$IP/cgi-bin/ -x md,js,html,php,py,css,txt -t 50
===============================================================
Gobuster v3.6
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://10.10.109.2/cgi-bin/
[+] Method:                  GET
[+] Threads:                 50
[+] Wordlist:                common.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.6
[+] Extensions:              js,html,php,py,css,txt,md
[+] Timeout:                 10s
===============================================================
Starting gobuster in directory enumeration mode
===============================================================
/printenv             (Status: 503) [Size: 299]
/test-cgi             (Status: 503) [Size: 299]
Progress: 37912 / 37912 (100.00%)
===============================================================
Finished
===============================================================
```

```bash
❯ curl http://$IP/cgi-bin/test-cgi
<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><head>
<title>503 Service Unavailable</title>
</head><body>
<h1>Service Unavailable</h1>
<p>The server is temporarily unable to service your
request due to maintenance downtime or capacity
problems. Please try again later.</p>
</body></html>
```


Time for googling apache vulns.
Apache httpd 2.4.49

And I found this:
<https://www.exploit-db.com/exploits/50383>

But of course it didn't worked for me beacuse im using latest version of curl.


You need to use --path-as-is flag to work.

```bash

```
