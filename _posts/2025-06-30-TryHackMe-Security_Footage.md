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

Hey there, fellow hackers and digital detectives! Today, we're diving into the [Security Footage](https://tryhackme.com/room/securityfootage) room on TryHackMe. This one is a fun forensics challenge where we get to play video editor with nothing but a network capture and a little bit of code.

Let's piece together this mystery, one frame at a time!

---

### Step 1: The Evidence File

First things first, download the provided file from the TryHackMe room. You'll get a `.pcap` file, which is a packet capture. Think of it as a recording of all the network conversations that were happening at a certain time. Our job is to eavesdrop on that conversation and find the secrets within.

### Step 2: A Manual Sneak Peek

If you open the `.pcap` file in a text editor like Neovim, VSCode, or even Notepad (you brave soul), you'll see a lot of what looks like gibberish. However, if you scroll through, you'll start to see a pattern.

You'll notice blocks of data that start with `JFIF` and are wrapped in what looks like HTTP multipart data, often ending with something like:

```
--BoundaryString
Content-type: image/jpeg
Content-Length: 10427
```

The `Content-type: image/jpeg` is a dead giveaway! The network traffic contains a stream of JPEG images. To prove our theory, let's try to extract just one of them by hand.

1.  Make a copy of the original file so we don't destroy our evidence.
    `cp security.pcap test.jpeg`
2.  Open `test.jpeg` in your favorite text editor. (I'm a Neovim fan myself, no text editor flame wars, please!)
3.  Carefully delete everything _except_ for the data that makes up a single image. A JPEG file in binary starts with the bytes `\xff\xd8` and ends with `\xff\xd9`. Find the first block of image data and surgically remove all the text and headers around it.
4.  Save the file and open it with any image viewer.

![Desktop View](2025-06-30-TryHackMe-Security_Footage/photo1.png){: width="1244" height="938" }

And voilà! Like magic, the first frame of the security footage appears. We're on the right track!

### Step 3: Automate It (Because We're Efficient!)

Now, doing that manually for what could be hundreds of frames would be a one-way ticket to carpal tunnel. No, thank you. As all good hackers do, let's automate the boring stuff.

I've whipped up a simple Python script to do the heavy lifting. This script will read the entire `.pcap` file, hunt for the start (`\xff\xd8`) and end (`\xff\xd9`) markers of each JPEG, carve them out, and save them as individual files.

```python
import os

# The name of the downloaded packet capture file
pcap_file = "input.pcap"

# The directory where we'll save our extracted images
output_dir = "extracted_jpegs"
os.makedirs(output_dir, exist_ok=True)

# These are the hexadecimal "magic numbers" for the start and end of a JPEG file.
jpeg_start = b'\xff\xd8'
jpeg_end = b'\xff\xd9'

print(f"[*] Reading the pcap file: {pcap_file}")
with open(pcap_file, 'rb') as f:
    data = f.read()

print("[*] Starting JPEG extraction...")
index = 0
offset = 0

# Loop through the file data to find all JPEGs
while True:
    # Find the start of the next JPEG
    start_idx = data.find(jpeg_start, offset)
    if start_idx == -1:
        break # No more JPEGs found!

    # Find the end of that same JPEG
    end_idx = data.find(jpeg_end, start_idx)
    if end_idx == -1:
        break # Found a start but no end, something is wrong.

    # The end marker itself is 2 bytes long, so we include it.
    end_idx += 2

    # Slice the JPEG data out of the main file
    jpeg_data = data[start_idx:end_idx]

    # Save the JPEG data to a new file with a padded name (e.g., image_00001.jpg)
    filename = os.path.join(output_dir, f'image_{index:05d}.jpg')
    with open(filename, 'wb') as img_file:
        img_file.write(jpeg_data)
        print(f"[+] {filename} has been saved.")

    # Move to the next frame and continue the search from where we left off
    index += 1
    offset = end_idx

print(f"\n[+] Success! Extracted {index} images to the '{output_dir}' directory.")
```

Run this script in the same directory as your `.pcap` file. It will create a new folder called `extracted_jpegs` and fill it with all the frames from the video.

### Step 4: Movie Time!

We have the frames, but we need a video. Enter our favorite command-line video wizard: `ffmpeg`. This powerful tool can stitch our pile of images back into a coherent video file.

Run the following command in your terminal:

```bash
ffmpeg -framerate 25 -i extracted_jpegs/image_%05d.jpg -c:v libx264 -pix_fmt yuv420p output.mp4
```

And... scene! You should now have an `output.mp4` file. Open it up, watch the security footage, and you'll find the flag you've been looking for.

Good luck, and happy hacking!
