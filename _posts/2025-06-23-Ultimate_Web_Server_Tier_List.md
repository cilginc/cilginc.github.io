---
title: "Ultimate Web Server Tier List"
author: cilgin
date: 2025-06-23 21:24:11 +0300
categories: [Tier List]
tags: [Web_Server, Tier_List]
pin: true
math: false
mermaid: false
image:
  path: /assets/img/2025-06-23-Ultimate_Web_Server_Tier_List/main.jpg
---

Welcome to the ultimate showdown of web servers. Where bytes meet bragging rights and request handling gets real. In this post, we slice and dice popular web servers based on hardcore metrics. From battle-tested veterans that power the internet’s backbone to scrappy upstarts trying to steal the spotlight, I’ll rank them into tiers so you know exactly which server deserves a throne and which one should probably stick to serving cat memes on a side project. Buckle up—it’s going to be a nerdy.

---

# The Web Servers I Tested

- Production

  - Nginx
  - Caddy
  - Apache
  - lighttpd
  - h2o

- Local Testing

  - node
  - python

- I (tried to) write a web server myself

  - rust
  - go

## Tools I used

I tested these servers on my machine, I know this is not a perfect test beacause it's not running in the cloud. Anyways here's the tools that i used:

- `k6` for testing
- `influxdb` for database
- `grafana` for monitoring
- `docker-compose` for infustructure

I served a simple production ready website. Here is the site i used <https://github.com/daidr/dualsense-tester>

I could've used kubernetes but I don't have time for that.
I maked the test for pushing the webservers to his limits. Here's the script that i used:

```js
import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  // This executor ramps up VUs from a starting point to a target over a duration.
  // It's designed to find the breaking point of a system.
  executor: "ramping-vus",

  // Start with 0 VUs.
  startVUs: 0,

  // Define the ramping profile.
  stages: [
    // Ramp from 0 to 5000 VUs over 5 minutes.
    { duration: "5m", target: 5000 }
  ],

  // Thresholds are CRITICAL here. They will automatically stop the test
  // when a server is considered "broken", giving us our result.
  thresholds: {
    // Abort the test if the error rate exceeds 2%. A server that's failing
    // this often is already broken.
    http_req_failed: [{ threshold: "rate<0.02", abortOnFail: true }],

    // Abort if the 95th percentile response time is over 1 second.
    // A 1-second response for a static file means the server is overloaded.
    http_req_duration: [{ threshold: "p(95)<1000", abortOnFail: true }]
  }
};

export default function () {
  const baseUrl = __ENV.BASE_URL || "http://localhost";
  const serverName = __ENV.SERVER_NAME || "unknown_server";

  const res = http.get(`${baseUrl}/index.html`, {
    tags: {
      server: serverName
    }
  });

  check(res, {
    "status is 200": (r) => r.status === 200
  });

  // A very short sleep is okay here as we are trying to maximize pressure.
  sleep(0.5);
}
```

Some people reading the code may be saw that I runned the tests for 5 minutes. I know It should be more but It doesn't even matter anyways.

# Production Servers

Production servers should have more features than just serving the static files. Such as HTTP/3 support. Firstly I compare the features and show you the performance tests that i runned.

## Features

| features | nginx   | Caddy   | Apache  | lighttpd | h2o            |
| -------- | ------- | ------- | ------- | -------- | -------------- |
| HTTP/3   | **Yes** | **Yes** | no      | no       | _experimental_ |
| QUIC     | **Yes** | **Yes** | no      | no       | _experimental_ |
| TLS      | **Yes** | **Yes** | **Yes** | **Yes**  | **Yes**        |
| Auto SSL | no      | **Yes** | no      | no       | no             |
| HTTP/2   | **Yes** | **Yes** | **Yes** | **Yes**  | **Yes**        |

Looks like the best option is `Caddy` for feature wise with auto SSL support.

## Performance Tests

### NGINX

![Desktop View](/assets/img/2025-06-23-Ultimate_Web_Server_Tier_List/nginx/photo1.png){: width="930" height="385" }
![Desktop View](/assets/img/2025-06-23-Ultimate_Web_Server_Tier_List/nginx/photo2.png){: width="936" height="393" }
![Desktop View](/assets/img/2025-06-23-Ultimate_Web_Server_Tier_List/nginx/photo3.png){: width="935" height="374" }
![Desktop View](/assets/img/2025-06-23-Ultimate_Web_Server_Tier_List/nginx/photo4.png){: width="928" height="383" }
![Desktop View](/assets/img/2025-06-23-Ultimate_Web_Server_Tier_List/nginx/photo5.png){: width="945" height="382" }

As you thought nginx have pretty good performance with good average response time.

### CADDY

![Desktop View](/assets/img/2025-06-23-Ultimate_Web_Server_Tier_List/caddy/photo1.png){: width="925" height="379" }
![Desktop View](/assets/img/2025-06-23-Ultimate_Web_Server_Tier_List/caddy/photo2.png){: width="926" height="381" }
![Desktop View](/assets/img/2025-06-23-Ultimate_Web_Server_Tier_List/caddy/photo3.png){: width="929" height="383" }
![Desktop View](/assets/img/2025-06-23-Ultimate_Web_Server_Tier_List/caddy/photo4.png){: width="928" height="390" }
![Desktop View](/assets/img/2025-06-23-Ultimate_Web_Server_Tier_List/caddy/photo5.png){: width="927" height="387" }

Caddy is making better than i thought and it is very close to nginx.

### APACHE

![Desktop View](/assets/img/2025-06-23-Ultimate_Web_Server_Tier_List/apache/photo1.png){: width="927" height="384" }
![Desktop View](/assets/img/2025-06-23-Ultimate_Web_Server_Tier_List/apache/photo2.png){: width="932" height="389" }
![Desktop View](/assets/img/2025-06-23-Ultimate_Web_Server_Tier_List/apache/photo3.png){: width="928" height="384" }
![Desktop View](/assets/img/2025-06-23-Ultimate_Web_Server_Tier_List/apache/photo4.png){: width="926" height="381" }
![Desktop View](/assets/img/2025-06-23-Ultimate_Web_Server_Tier_List/apache/photo5.png){: width="937" height="388" }

Apache gets demolished by the best with around **7000** HTTP failures and **1 minutes** of max response time.
You shouldn't use apache in 2025.

### LIGHTTPD

![Desktop View](/assets/img/2025-06-23-Ultimate_Web_Server_Tier_List/lighttpd/photo1.png){: width="941" height="380" }
![Desktop View](/assets/img/2025-06-23-Ultimate_Web_Server_Tier_List/lighttpd/photo2.png){: width="935" height="383" }
![Desktop View](/assets/img/2025-06-23-Ultimate_Web_Server_Tier_List/lighttpd/photo3.png){: width="932" height="381" }
![Desktop View](/assets/img/2025-06-23-Ultimate_Web_Server_Tier_List/lighttpd/photo4.png){: width="937" height="377" }
![Desktop View](/assets/img/2025-06-23-Ultimate_Web_Server_Tier_List/lighttpd/photo5.png){: width="930" height="378" }

I never heard of this web server before but I think its perfoming better than apache. You shouldn't use this server on production tho.

### H2O

![Desktop View](/assets/img/2025-06-23-Ultimate_Web_Server_Tier_List/h2o/photo1.png){: width="917" height="378" }
![Desktop View](/assets/img/2025-06-23-Ultimate_Web_Server_Tier_List/h2o/photo2.png){: width="924" height="388" }
![Desktop View](/assets/img/2025-06-23-Ultimate_Web_Server_Tier_List/h2o/photo3.png){: width="934" height="377" }
![Desktop View](/assets/img/2025-06-23-Ultimate_Web_Server_Tier_List/h2o/photo4.png){: width="932" height="379" }
![Desktop View](/assets/img/2025-06-23-Ultimate_Web_Server_Tier_List/h2o/photo5.png){: width="936" height="380" }

I never heard of this one it perfoms the worst of all of them. There is no reason to use webser on production.

## Winner

I think there are two winners:

- `Nginx` and `Caddy`

I think caddy is great for newcomers with easy configuration and great documentation. And It is very close to nginx.
Real production king is `Nginx` of course but I will not use `Nginx` in every project after this test. beacause for smaller projects `Caddy` can work like a charm too.

# Local Servers

You don't want much for a local testing server. Just serve the files rigth. I am not doing that and pushing the limits of these servers. There are 2 main local web servers:

- `python -m http.server`
- `npx http-server`

`Python` didn't survive the tests.

I'm making this test for just curiousity. Use whatever you like. I like python one more.

### Python

![Desktop View](/assets/img/2025-06-23-Ultimate_Web_Server_Tier_List/python/photo1.png){: width="937" height="382" }
![Desktop View](/assets/img/2025-06-23-Ultimate_Web_Server_Tier_List/python/photo2.png){: width="935" height="386" }
![Desktop View](/assets/img/2025-06-23-Ultimate_Web_Server_Tier_List/python/photo3.png){: width="927" height="380" }
![Desktop View](/assets/img/2025-06-23-Ultimate_Web_Server_Tier_List/python/photo4.png){: width="943" height="384" }
![Desktop View](/assets/img/2025-06-23-Ultimate_Web_Server_Tier_List/python/photo5.png){: width="932" height="385" }

Python didn't finished the test. It is not that performant like other servers.

### Node

![Desktop View](/assets/img/2025-06-23-Ultimate_Web_Server_Tier_List/node/photo1.png){: width="932" height="385" }
![Desktop View](/assets/img/2025-06-23-Ultimate_Web_Server_Tier_List/node/photo2.png){: width="923" height="388" }
![Desktop View](/assets/img/2025-06-23-Ultimate_Web_Server_Tier_List/node/photo3.png){: width="931" height="382" }
![Desktop View](/assets/img/2025-06-23-Ultimate_Web_Server_Tier_List/node/photo4.png){: width="937" height="383" }
![Desktop View](/assets/img/2025-06-23-Ultimate_Web_Server_Tier_List/node/photo5.png){: width="932" height="382" }

Node server performance overkill for its use. But it is faster than some of the production servers.

## Winner

Winner is your preferrence of course.
For small VUS 2 servers are nearly the same on performance side.
Use whatever you want.
You may want to use node beacause it is more stable.
You may want to use python beacause it is already installed.

# Servers that I wrote

This section is only for fun never blame me for anything. I just tried to serve a website with using libraries.
And It sucked as you probably thought.

I used default http library with `go` and used warp with `rust`.

`Rust` one didn't survive the tests but at least it works.
`Go` one maked a lot of HTTP failures not beacause the default go library is bad beacause my code suck.

### Go

![Desktop View](/assets/img/2025-06-23-Ultimate_Web_Server_Tier_List/go/photo1.png){: width="906" height="385" }
![Desktop View](/assets/img/2025-06-23-Ultimate_Web_Server_Tier_List/go/photo2.png){: width="905" height="392" }
![Desktop View](/assets/img/2025-06-23-Ultimate_Web_Server_Tier_List/go/photo3.png){: width="908" height="381" }
![Desktop View](/assets/img/2025-06-23-Ultimate_Web_Server_Tier_List/go/photo4.png){: width="906" height="390" }
![Desktop View](/assets/img/2025-06-23-Ultimate_Web_Server_Tier_List/go/photo5.png){: width="911" height="387" }

If you look at the graphs you may see that go is made 16000796 requests which is higher than nginx. But if you look at the http failures you will see 800612 failures. If my code doesn't suck there will be probably around 800184 requests made. Which is not bad for a go library.

### Rust

![Desktop View](/assets/img/2025-06-23-Ultimate_Web_Server_Tier_List/rust/photo1.png){: width="928" height="389" }
![Desktop View](/assets/img/2025-06-23-Ultimate_Web_Server_Tier_List/rust/photo2.png){: width="930" height="378" }
![Desktop View](/assets/img/2025-06-23-Ultimate_Web_Server_Tier_List/rust/photo3.png){: width="931" height="380" }
![Desktop View](/assets/img/2025-06-23-Ultimate_Web_Server_Tier_List/rust/photo4.png){: width="928" height="379" }
![Desktop View](/assets/img/2025-06-23-Ultimate_Web_Server_Tier_List/rust/photo5.png){: width="928" height="379" }

Rust didn't completed the test. I don't think my code suck at this point. I think rust http libraries not good as you think. Just joking don't rewrite nginx with rust please.

# Last Thoughts

This experiment is good for my curiousity. Before i maked the test i was always using nginx. But now i may be use caddy on smaller projects. For production just use `nginx` it is the default and best web server of all time. 

Thank you for reading me. I hope this blog post was useful to you.
