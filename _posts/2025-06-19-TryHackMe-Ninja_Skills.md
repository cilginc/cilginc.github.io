---
title: "TryHackMe: Hacker vs Hacker"
author: cilgin
date: 2025-06-20 00:16:13 +0300
categories: [CyberSecurity]
tags: [CTF, TryHackMe, Easy]
pin: true
math: false
mermaid: false
image:
  path: /assets/img/2025-06-18-TryHackMe-Ninja_Skills.md/Ninja_Skills.md
---

# SSH'ing into machine

Start by ssh'ing to machine:

- user: new-user
- password: new-user

```bash
ssh new-user@10.10.194.46
```

## Question 1

Which of the above files are owned by the best-group group(enter the answer separated by spaces in alphabetical order)

---

We can use this command to search that files:

```bash
find / -type f \( -name '8V2L' -o -name 'bny0' -o -name 'c4ZX' -o -name 'D8B3' -o -name 'FHl1' -o -name 'oiMO' -o -name 'PFbD' -o -name 'rmfX' -o -name 'SRSq' -o -name 'uqyw' -o -name 'v2Vb' -o -name 'X1Uy' \) -group best-group 2>/dev/null
```

## Question 2

Which of these files contain an IP address?

---

We firstly need to get all the paths for these files and save somewhere on the file system.
To do that:

```bash
find / -type f \( -name '8V2L' -o -name 'bny0' -o -name 'c4ZX' -o -name 'D8B3' -o -name 'FHl1' -o -name 'oiMO' -o -name 'PFbD' -o -name 'rmfX' -o -name 'SRSq' -o -name 'uqyw' -o -name 'v2Vb' -o -name 'X1Uy' \) 2>/dev/null > paths.txt
```

And then now we got the file paths. We can get the files with ip addresses with this command:

```bash
grep  -Eo "([0-9]{1,3}[\.]){3}[0-9]{1,3}" $(<paths.txt)
```

## Question 3

Which file has the SHA1 hash of 9d54da7584015647ba052173b84d45e8007eba94

---

I wrote a script for finding file with the given hash:

```bash
#!/bin/bash

target_hash="9d54da7584015647ba052173b84d45e8007eba94"

while IFS= read -r file; do
  if [ -f "$file" ]; then
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

Which file contains 230 lines?

---

I also wrote a script for that too. It very close to first script but it works.

```bash
#!/bin/bash

target_lines=230

while IFS= read -r file; do
  if [ -f "$file" ]; then
    line_count=$(wc -l < "$file")
    if [ "$line_count" -eq "$target_lines" ]; then
      echo "Match found: $file"
    fi
  fi
done < paths.txt
```

Also this script is not gonna work beacuse every file on the `paths.txt`{: .filepath} files is 209 lines long.
There is only one file that are not in the `paths.txt`{: .filepath} should be it then.

## Question 5

Which file's owner has an ID of 502?

---

Yes, I could've make a script for this but since there are not many files. I use my eyes for finding the files.

```bash
[new-user@ip-10-10-194-46 ~]$ cat paths.txt | xargs ls -ln
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

Which file is executable by everyone?

---

Same Thing happens on this question. I use my eyes bla bla.

```bash
[new-user@ip-10-10-194-46 ~]$ cat paths.txt | xargs ls -ln
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
