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
