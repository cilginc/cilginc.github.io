---
title: "TryHackMe: Ninja Skills"
author: cilgin
date: 2025-06-20 00:16:13 +0300
categories: [CyberSecurity]
tags: [CTF, TryHackMe, Easy]
pin: false
math: false
mermaid: false
image:
  path: /assets/img/2025-06-18-TryHackMe-Ninja_Skills/Ninja_Skills.webp
---

Howdy, fellow hackers! This is my walkthrough for the [Ninja Skills](https://tryhackme.com/room/ninjaskills) room on TryHackMe. Join me as I slice and dice my way through the challenges to capture the flags.

# SSH'ing into the Machine

First things first, let's get a shell on the box. The credentials are nice and simple:

- **User:** `new-user`
- **Password:** `new-user`

Let's SSH in:

```bash
ssh new-user@10.10.194.46
```

## Question 1

**Which of the above files are owned by the `best-group` group (enter the answer separated by spaces in alphabetical order)?**

---

Time to put our `find` command to work. We can use this one-liner to track down the files we need. It's a bit of a beast, but it gets the job done!

```bash
# This command searches the entire filesystem (-type f) for any file
# with one of the given names (-name '8V2L' -o ...).
# It then filters for files belonging to the 'best-group' (-group best-group).
# The '2>/dev/null' part just hides any pesky "Permission denied" errors.
find / -type f \( -name '8V2L' -o -name 'bny0' -o -name 'c4ZX' -o -name 'D8B3' -o -name 'FHl1' -o -name 'oiMO' -o -name 'PFbD' -o -name 'rmfX' -o -name 'SRSq' -o -name 'uqyw' -o -name 'v2Vb' -o -name 'X1Uy' \) -group best-group 2>/dev/null
```

## Question 2

**Which of these files contain an IP address?**

---

First, we need a list of all the possible files. Let's use our `find` command again, but this time, we'll save the results to a handy file called `paths.txt`.

```bash
find / -type f \( -name '8V2L' -o -name 'bny0' -o -name 'c4ZX' -o -name 'D8B3' -o -name 'FHl1' -o -name 'oiMO' -o -name 'PFbD' -o -name 'rmfX' -o -name 'SRSq' -o -name 'uqyw' -o -name 'v2Vb' -o -name 'X1Uy' \) 2>/dev/null > paths.txt
```

Now that we have our list, we can unleash `grep` to hunt for IP addresses within those files.

```bash
# We use grep with a regex to find anything that looks like an IP address.
# The $(<paths.txt) part cleverly feeds the contents of our file list to grep.
grep -Eo "([0-9]{1,3}[\.]){3}[0-9]{1,3}" $(<paths.txt)
```

## Question 3

**Which file has the SHA1 hash of `9d54da7584015647ba052173b84d45e8007eba94`?**

---

This calls for a custom script! I whipped up this little Bash beauty to loop through our `paths.txt` file and check the SHA1 hash of each file until it finds a match.

```bash
#!/bin/bash

target_hash="9d54da7584015647ba052173b84d45e8007eba94"

while IFS= read -r file; do
  if [ -f "$file" ]; then
    # Calculate the hash and compare it to our target
    hash=$(sha1sum "$file" | awk '{print $1}')
    if [[ "$hash" == "$target_hash" ]]; then
      echo "Match found: $file"
      exit 0
    fi
  fi
done < paths.txt

echo "No match found."
```

## Question 4

**Which file contains 230 lines?**

---

You know the drill by now... time for another script! It's very similar to the last one, but hey, if it ain't broke, don't fix it.

```bash
#!/bin/bash

target_lines=230

while IFS= read -r file; do
  if [ -f "$file" ]; then
    # Count the lines and see if we have a winner
    line_count=$(wc -l < "$file")
    if [ "$line_count" -eq "$target_lines" ]; then
      echo "Match found: $file"
    fi
  fi
done < paths.txt
```

**Plot twist!** This script isn't going to work. It turns out every single file in our `paths.txt` list is 209 lines long. That means the file we're looking for is the one that _isn't_ on our list. Sneaky, sneaky!

## Question 5

**Which file's owner has an ID of 502?**

---

Okay, I _could_ have made another script for this, but with such a short list of files, the good ol' "eyeball-o-scope" is the fastest tool in the shed. Let's just `ls` them and see.

```bash
$ cat paths.txt | xargs ls -ln
-rwxrwxr-x 1 501 501 13545 Oct 23  2019 /etc/8V2L
-rw-rw-r-- 1 501 501 13545 Oct 23  2019 /etc/ssh/SRSq
-rw-rw-r-- 1 501 502 13545 Oct 23  2019 /home/v2Vb
-rw-rw-r-- 1 501 501 13545 Oct 23  2019 /media/rmfX
-rw-rw-r-- 1 501 501 13545 Oct 23  2019 /mnt/c4ZX
-rw-rw-r-- 1 501 502 13545 Oct 23  2019 /mnt/D8B3
-rw-rw-r-- 1 501 501 13545 Oct 23  2019 /opt/oiMO
-rw-rw-r-- 1 501 501 13545 Oct 23  2019 /opt/PFbD
-rw-rw-r-- 1 501 501 13545 Oct 23  2019 /var/FHl1
-rw-rw-r-- 1 501 501 13545 Oct 23  2019 /var/log/uqyw
-rw-rw-r-- 1 502 501 13545 Oct 23  2019 /X1Uy
```

## Question 6

**Which file is executable by everyone?**

---

And for our grand finale... you guessed it! We're using our trusty eyes again. The `ls -ln` output from the previous question has all the information we need. Just look for the `x` in the "others" permission slot.

```bash
$ cat paths.txt | xargs ls -ln
-rwxrwxr-x 1 501 501 13545 Oct 23  2019 /etc/8V2L
-rw-rw-r-- 1 501 501 13545 Oct 23  2019 /etc/ssh/SRSq
-rw-rw-r-- 1 501 502 13545 Oct 23  2019 /home/v2Vb
-rw-rw-r-- 1 501 501 13545 Oct 23  2019 /media/rmfX
-rw-rw-r-- 1 501 501 13545 Oct 23  2019 /mnt/c4ZX
-rw-rw-r-- 1 501 502 13545 Oct 23  2019 /mnt/D8B3
-rw-rw-r-- 1 501 501 13545 Oct 23  2019 /opt/oiMO
-rw-rw-r-- 1 501 501 13545 Oct 23  2019 /opt/PFbD
-rw-rw-r-- 1 501 501 13545 Oct 23  2019 /var/FHl1
-rw-rw-r-- 1 501 501 13545 Oct 23  2019 /var/log/uqyw
-rw-rw-r-- 1 502 501 13545 Oct 23  2019 /X1Uy
```
