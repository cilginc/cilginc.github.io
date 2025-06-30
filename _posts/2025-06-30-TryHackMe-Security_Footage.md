---
title: "TryHackMe: Security Footage"
author: cilgin
date: 2025-06-29 19:51:50 +0300
categories: [CyberSecurity]
tags: [CTF, TryHackMe, Medium]
pin: true
math: false
mermaid: false
image:
  path: /assets/img/2025-06-30-TryHackMe-Security_Footage/main.png
---

Hi I'm doing <https://tryhackme.com/room/securityfootage>

---


Firstly download the files.

You'll see a pcap file looks like this:

In this pcap you will see some image blocks which starts with JFIF and ends with 
--BoundaryString
Content-type: image/jpeg
Content-Length:     10427


So we can try to delete all the files expect one image block 
you can use whatever you want but i'll be using neovim

Copy the existing file and delete all the blocks expect first block.
Rename it to .jpeg

And open with your image viever software.

![Desktop View](2025-06-30-TryHackMe-Security_Footage/photo1.png){: width="972" height="589" }

And voila now you can see the first frame of the video.

But we can't manually get the all images right.

So I maked a python script for this:

```python
import os

pcap_file = "input.pcap" # Change this for yourself
output_dir = "extracted_jpegs"
os.makedirs(output_dir, exist_ok=True)

jpeg_start = b'\xff\xd8'
jpeg_end = b'\xff\xd9'

with open(pcap_file, 'rb') as f:
    data = f.read()

index = 0
offset = 0

while True:
    start_idx = data.find(jpeg_start, offset)
    if start_idx == -1:
        break
    end_idx = data.find(jpeg_end, start_idx)
    if end_idx == -1:
        break
    end_idx += 2  

    jpeg_data = data[start_idx:end_idx]
    filename = os.path.join(output_dir, f'image_{index:05d}.jpg')
    with open(filename, 'wb') as img_file:
        img_file.write(jpeg_data)
        print(f"[+] {filename} kaydedildi.")
    
    index += 1
    offset = end_idx
```


If you run this script you'll get all the images in the pcap file in extracted_jpegs directory

And we need to make this images a video with ffmpeg with this command:

```bash
ffmpeg -framerate 25 -i extracted_jpegs/image_%05d.jpg -c:v libx264 -pix_fmt yuv420p output.mp4
```

And you'll get output.mp4 which obtains flag for the room. Good luck typing every charecter by yourself.

