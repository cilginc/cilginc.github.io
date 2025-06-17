---
title: "TryHackMe: Hacker vs Hacker"
description: "**Hacker vs Hacker** is Easy CTF Room on TryHackMe."
author: cilgin
date: 2025-06-18 02:11:36 +0300
categories: [CyberSecurity]
tags: [CTF, TryHackMe, Easy]
pin: true
math: false
mermaid: false
image:
  path: /assets/img/2025-06-18-TryHackMe-Hacker_vs_Hacker/Hacker_vs_Hacker.png
  alt: Hacker vs Hacker picture.
---


# Enumeration

## Nmap Scan

I start with exporting the target machine IP adress as a enviroment variable:

```sh
export IP=10.10.160.10
```

And runnig `nmap` scan on the target:

```sh
nmap -T4 -n -sC -sV -Pn -p- $IP
Starting Nmap 7.97 ( https://nmap.org ) at 2025-06-18 02:16 +0300
Nmap scan report for 10.10.160.10
Host is up (0.071s latency).
Not shown: 65533 closed tcp ports (conn-refused)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.4 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 9f:a6:01:53:92:3a:1d:ba:d7:18:18:5c:0d:8e:92:2c (RSA)
|   256 4b:60:dc:fb:92:a8:6f:fc:74:53:64:c1:8c:bd:de:7c (ECDSA)
|_  256 83:d4:9c:d0:90:36:ce:83:f7:c7:53:30:28:df:c3:d5 (ED25519)
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 98.73 seconds
```
