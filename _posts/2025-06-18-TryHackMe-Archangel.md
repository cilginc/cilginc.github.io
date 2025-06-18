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
