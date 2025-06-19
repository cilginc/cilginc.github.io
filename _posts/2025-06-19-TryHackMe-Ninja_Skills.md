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
