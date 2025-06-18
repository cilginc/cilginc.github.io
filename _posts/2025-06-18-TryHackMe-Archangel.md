---
title: "TryHackMe: Archangel"
author: cilgin
date: 2025-06-18 00:38:49 +0300
categories: [CyberSecurity]
tags: [CTF, TryHackMe, Easy]
pin: true
math: false
mermaid: false
image:
  path: /assets/img/2025-06-18-TryHackMe-Archangel/Archangel.png
---

# Enumeration

## Nmap Scan

I start with exporting the target machine IP adress as a enviroment variable:

```bash
export IP=10.10.205.56
```

And runnig `nmap` scan on the target:

```bash
nmap -T4 -n -sC -sV -Pn -p- $IP
Starting Nmap 7.97 ( https://nmap.org ) at 2025-06-18 00:46 +0300
Nmap scan report for 10.10.178.245
Host is up (0.079s latency).
Not shown: 65533 closed tcp ports (conn-refused)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 9f:1d:2c:9d:6c:a4:0e:46:40:50:6f:ed:cf:1c:f3:8c (RSA)
|   256 63:73:27:c7:61:04:25:6a:08:70:7a:36:b2:f2:84:0d (ECDSA)
|_  256 b6:4e:d2:9c:37:85:d6:76:53:e8:c4:e0:48:1c:ae:6c (ED25519)
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 107.34 seconds
```
