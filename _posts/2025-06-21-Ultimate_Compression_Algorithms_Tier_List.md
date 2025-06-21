---
title: "Ultimate Compression Algorithms Tier List"
author: cilgin
date: 2025-06-21 21:58:41 +0300
categories: [Tier List]
tags: [Compression, Tier_List]
pin: true
math: false
mermaid: false
image:
  path: /assets/img/2025-06-21-Ultimate_Compression_Algorithms_Tier_List/main.png
---

This is a technical blog post about compression algorithms. Stay tuned to find which is the best algorithm for your needs.

---

# What is Data Compression?

**Data compression** is the process of encoding information using fewer bits than the original representation. Its goal is to reduce file size for efficient storage, faster transmission, or both.

There are two main categories of compression:

- **Lossless Compression**: Preserves all original data. The decompressed output is bit-for-bit identical to the input. Common algorithms include `DEFLATE` (used in gzip), `bzip2`, `LZMA`, and `Zstandard`.
- **Lossy Compression**: Sacrifices some data accuracy to achieve higher compression ratios. Used for audio, image, and video (e.g., MP3, JPEG, H.264).

Compression algorithms often rely on techniques such as:

- **Entropy encoding** (e.g. Huffman, arithmetic coding)
- **Dictionary-based compression** (e.g. LZ77, LZ78)
- **Prediction models and context modeling** (used in modern compressors like Zstandard or paq8)

The effectiveness of compression depends on data type, redundancy level, and the algorithm’s design trade-offs between speed, memory usage, and compression ratio.

# Testing the Algorithms

I tested these algorithms on this blog post:

- gzip
- bzip2
- xz
- zstd
- lz4
- brotli
- lzma (7zip)
- zip

Here's the all versions I tested:

```text
gzip 1.14-modified
bzip2, a block-sorting file compressor.  Version 1.0.8, 13-Jul-2019.
xz (XZ Utils) 5.8.1
*** Zstandard CLI (64-bit) v1.5.7, by Yann Collet ***
*** lz4 v1.10.0 64-bit multithread, by Yann Collet ***
brotli 1.1.0
liblzma 5.8.1
This is Zip 3.0 (July 5th 2008), by Info-ZIP.
```

## Files I tested

- Flight data on <https://www.tablab.app/json/sample>
- OpenSSH logs on <https://github.com/logpai/loghub
- <https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt>
- My FLAC library

### Flight Data JSON

- File Size: 123.0 MB

![Desktop View](/assets/img/2025-06-21-Ultimate_Compression_Algorithms_Tier_List/photo1.png){: width="700" height="500" }

![Desktop View](/assets/img/2025-06-21-Ultimate_Compression_Algorithms_Tier_List/photo2.png){: width="700" height="500" }

![Desktop View](/assets/img/2025-06-21-Ultimate_Compression_Algorithms_Tier_List/photo3.png){: width="700" height="500" }

The winner is `bzip2` for JSON files. Best compression ratio of all ones with good compression times. Only downside is that decompression times is not good as others.

### OpenSSH Logs

- File Size: 73.4 MB

![Desktop View](/assets/img/2025-06-21-Ultimate_Compression_Algorithms_Tier_List/photo4.png){: width="700" height="500" }

![Desktop View](/assets/img/2025-06-21-Ultimate_Compression_Algorithms_Tier_List/photo5.png){: width="700" height="500" }

![Desktop View](/assets/img/2025-06-21-Ultimate_Compression_Algorithms_Tier_List/photo6.png){: width="700" height="500" }

The winner is `bzip2` again for sure. If I'm writing a log backup script i definitely use `bzip2`. I think `bzip2` is good at plain text with repeated symbols.

### rockyou.txt

- File Size: 139.9 MB

![Desktop View](/assets/img/2025-06-21-Ultimate_Compression_Algorithms_Tier_List/photo7.png){: width="700" height="500" }

![Desktop View](/assets/img/2025-06-21-Ultimate_Compression_Algorithms_Tier_List/photo8.png){: width="700" height="500" }

![Desktop View](/assets/img/2025-06-21-Ultimate_Compression_Algorithms_Tier_List/photo9.png){: width="700" height="500" }

On `rockyou.txt` `bzip2` is performing very badly and compression ratio is nearly same as `zstd`which makes `bzip2` worst algorithm for rockyou.txt. I think `zstd` did a very great job here not the best compression ratio but it's very fast. But the winner is `xz` or `lzma` here. 

### FLAC Songs

I used 3 albums from my library. Even thought FLAC's are compressed we can try to compress them even more with these algorithms.
I needed to make the 3 albums on the same file for algorithms to work.

Tools I used:

```text
tar (GNU tar) 1.35
```

- File Size: 3.6 GB

![Desktop View](/assets/img/2025-06-21-Ultimate_Compression_Algorithms_Tier_List/photo10.png){: width="700" height="500" }

![Desktop View](/assets/img/2025-06-21-Ultimate_Compression_Algorithms_Tier_List/photo11.png){: width="700" height="500" }

![Desktop View](/assets/img/2025-06-21-Ultimate_Compression_Algorithms_Tier_List/photo12.png){: width="700" height="500" }

And as you can see from the graphs we can't compress FLAC more with these algorithms. Just never try to compress FLAC's like me or you will end up with waste of time.

# Last Thoughts

These been a great experiment for me. I think using zip on linux is not a good solution because gzip is better and open source. My favorite one on this list `zstd` of course. Because it's very very fast. And you know sometimes you need to transfer some big files over your home network. And you have enough file space. If you are using gigabit ethernet, I think compressing with `zstd` will speed up the process. I also like `xz` beacuse I't have the smallest file size (I'm ignoring `brotli` it is too slow). I think `brotli` is not bad for homelabs. You know there is a computers that doing nothing but a running some webservers. Just give a `brotli` compression and the whole month will be 100% CPU. It can be worth the waiting. Anyways here is my go to algorithms for tasks:

- Sharing archive on public: `brotli`
- If you don't like waiting: `xz`
- Log backups and json: `bzip2`
- If file size is under `10G` and I don't know which algorithm is best for that file: `gzip`
- Same thing but if it is over `10G`: `zstd`

You can use your own defaults, just inspect the charts and pick one for your needs.

Thank you for reading me. I hope this blog post was useful to you.
