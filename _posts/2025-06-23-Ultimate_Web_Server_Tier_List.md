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

Welcome to the ultimate showdown of web servers, where bytes meet bragging rights and request handling gets real. In this post, we'll slice and dice popular web servers based on hardcore metrics. From battle-tested veterans that power the internet’s backbone to scrappy upstarts trying to steal the spotlight, I’ll rank them into tiers so you know exactly which server deserves a throne and which one should probably stick to serving cat memes on a side project. Buckle up—it’s going to be a nerdy ride.

---

# The Web Servers I Tested

### Production

- Nginx
- Caddy
- Apache
- Lighttpd
- H2O

### Local Testing

- Node.js (`http-server`)
- Python (`http.server`)

### I (Tried to) Write a Web Server Myself

- Rust
- Go

## Tools I Used

I tested these servers on my local machine. I know this isn't a perfect test because it's not running in a controlled cloud environment, but it's a great way to push them to their limits.

Anyway, here are the tools I used:

- `k6` for load testing
- `InfluxDB` for the database
- `Grafana` for monitoring
- `docker-compose` for infrastructure

I served a simple, production-ready website. Here is the site I used: [dualsense-tester](https://github.com/daidr/dualsense-tester).

I could've used Kubernetes, but I don't have time for that.

I designed the test to push the web servers to their limits. Here's the k6 script I used:

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

Some of you reading the code might have noticed that I ran the tests for only 5 minutes. I know it should ideally be longer, but for finding a server's breaking point, five minutes is plenty of time to see the cracks appear.

# Production Servers

Production servers need more than just the ability to serve static files, such as support for modern protocols like HTTP/3. First, let's compare their features, then we'll dive into the performance tests I ran.

## Features

| Feature  | Nginx   | Caddy   | Apache  | Lighttpd | H2O              |
| :------- | :------ | :------ | :------ | :------- | :--------------- |
| HTTP/3   | **Yes** | **Yes** | No      | No       | _(experimental)_ |
| QUIC     | **Yes** | **Yes** | No      | No       | _(experimental)_ |
| TLS      | **Yes** | **Yes** | **Yes** | **Yes**  | **Yes**          |
| Auto SSL | No      | **Yes** | No      | No       | No               |
| HTTP/2   | **Yes** | **Yes** | **Yes** | **Yes**  | **Yes**          |

Feature-wise, `Caddy` looks like the clear winner with its built-in automatic SSL support.

## Performance Tests

### NGINX

![Desktop View](/assets/2025-06-23-Ultimate_Web_Server_Tier_List/nginx/photo1.png){: width="930" height="385" }
![Desktop View](/assets/2025-06-23-Ultimate_Web_Server_Tier_List/nginx/photo2.png){: width="936" height="393" }
![Desktop View](/assets/2025-06-23-Ultimate_Web_Server_Tier_List/nginx/photo3.png){: width="935" height="374" }
![Desktop View](/assets/2025-06-23-Ultimate_Web_Server_Tier_List/nginx/photo4.png){: width="928" height="383" }
![Desktop View](/assets/2025-06-23-Ultimate_Web_Server_Tier_List/nginx/photo5.png){: width="945" height="382" }

As you might expect, Nginx has pretty good performance with a great average response time.

### CADDY

![Desktop View](/assets/2025-06-23-Ultimate_Web_Server_Tier_List/caddy/photo1.png){: width="925" height="379" }
![Desktop View](/assets/2025-06-23-Ultimate_Web_Server_Tier_List/caddy/photo2.png){: width="926" height="381" }
![Desktop View](/assets/2025-06-23-Ultimate_Web_Server_Tier_List/caddy/photo3.png){: width="929" height="383" }
![Desktop View](/assets/2025-06-23-Ultimate_Web_Server_Tier_List/caddy/photo4.png){: width="928" height="390" }
![Desktop View](/assets/2025-06-23-Ultimate_Web_Server_Tier_List/caddy/photo5.png){: width="927" height="387" }

Caddy performed better than I thought and is very close to Nginx's performance.

### APACHE

![Desktop View](/assets/2025-06-23-Ultimate_Web_Server_Tier_List/apache/photo1.png){: width="927" height="384" }
![Desktop View](/assets/2025-06-23-Ultimate_Web_Server_Tier_List/apache/photo2.png){: width="932" height="389" }
![Desktop View](/assets/2025-06-23-Ultimate_Web_Server_Tier_List/apache/photo3.png){: width="928" height="384" }
![Desktop View](/assets/2025-06-23-Ultimate_Web_Server_Tier_List/apache/photo4.png){: width="926" height="381" }
![Desktop View](/assets/2025-06-23-Ultimate_Web_Server_Tier_List/apache/photo5.png){: width="937" height="388" }

Apache gets demolished, clocking in with around **7,000** HTTP failures and a max response time of **1 minute**. You probably shouldn't be using Apache for this kind of workload in 2025.

### LIGHTTPD

![Desktop View](/assets/2025-06-23-Ultimate_Web_Server_Tier_List/lighttpd/photo1.png){: width="941" height="380" }
![Desktop View](/assets/2025-06-23-Ultimate_Web_Server_Tier_List/lighttpd/photo2.png){: width="935" height="383" }
![Desktop View](/assets/2025-06-23-Ultimate_Web_Server_Tier_List/lighttpd/photo3.png){: width="932" height="381" }
![Desktop View](/assets/2025-06-23-Ultimate_Web_Server_Tier_List/lighttpd/photo4.png){: width="937" height="377" }
![Desktop View](/assets/2025-06-23-Ultimate_Web_Server_Tier_List/lighttpd/photo5.png){: width="930" height="378" }

I had never heard of this web server before, but it performs better than Apache. I still wouldn't recommend it for production, though.

### H2O

![Desktop View](/assets/2025-06-23-Ultimate_Web_Server_Tier_List/h2o/photo1.png){: width="917" height="378" }
![Desktop View](/assets/2025-06-23-Ultimate_Web_Server_Tier_List/h2o/photo2.png){: width="924" height="388" }
![Desktop View](/assets/2025-06-23-Ultimate_Web_Server_Tier_List/h2o/photo3.png){: width="934" height="377" }
![Desktop View](/assets/2025-06-23-Ultimate_Web_Server_Tier_List/h2o/photo4.png){: width="932" height="379" }
![Desktop View](/assets/2025-06-23-Ultimate_Web_Server_Tier_List/h2o/photo5.png){: width="936" height="380" }

I'd also never heard of this one, and it performed the worst of them all. There's no reason to use this web server in production.

## Winner

I think there are two winners:

- `Nginx` and `Caddy`

Caddy is great for newcomers with its easy configuration and fantastic documentation. Performance-wise, it's very close to Nginx.

The real production king is still `Nginx`, of course, but after this test, I won't be reaching for it for _every_ project. For smaller projects, `Caddy` can work like a charm.

# Local Servers

You don't need much from a local testing server. Just serve the files, right? Well, I decided to ignore that and push these servers to their limits anyway. The two main contenders are:

- `python -m http.server`
- `npx http-server` (a popular Node.js package)

I'm doing this test purely out of curiosity. You should use whichever you prefer. I'm personally a fan of the Python one for its sheer simplicity.

### Python

![Desktop View](/assets/2025-06-23-Ultimate_Web_Server_Tier_List/python/photo1.png){: width="937" height="382" }
![Desktop View](/assets/2025-06-23-Ultimate_Web_Server_Tier_List/python/photo2.png){: width="935" height="386" }
![Desktop View](/assets/2025-06-23-Ultimate_Web_Server_Tier_List/python/photo3.png){: width="927" height="380" }
![Desktop View](/assets/2025-06-23-Ultimate_Web_Server_Tier_List/python/photo4.png){: width="943" height="384" }
![Desktop View](/assets/2025-06-23-Ultimate_Web_Server_Tier_List/python/photo5.png){: width="932" height="385" }

Python's built-in server didn't finish the test. It's clearly not as performant as the others, which is expected.

### Node.js

![Desktop View](/assets/2025-06-23-Ultimate_Web_Server_Tier_List/node/photo1.png){: width="932" height="385" }
![Desktop View](/assets/2025-06-23-Ultimate_Web_Server_Tier_List/node/photo2.png){: width="923" height="388" }
![Desktop View](/assets/2025-06-23-Ultimate_Web_Server_Tier_List/node/photo3.png){: width="931" height="382" }
![Desktop View](/assets/2025-06-23-Ultimate_Web_Server_Tier_List/node/photo4.png){: width="937" height="383" }
![Desktop View](/assets/2025-06-23-Ultimate_Web_Server_Tier_List/node/photo5.png){: width="932" height="382" }

The Node.js server's performance is overkill for its typical use case. It's even faster than some of the production servers we tested!

## Winner

The winner here is your personal preference, of course. For a small number of users, the two servers are nearly identical in performance.

- You might want to use the **Node.js server** because it's more stable under load.
- You might want to use the **Python server** because it comes pre-installed on most systems.

# Servers That I Wrote

This section is just for fun, so don't judge my coding skills too harshly! I tried to build a simple web server using standard libraries to see what would happen. And, as you probably guessed, the results were... not great.

I used the default `http` library with `Go` and the `warp` framework with `Rust`.

My `Go` server had a lot of HTTP failures—not because the default library is bad, but because my code sucks. The `Rust` one didn't even survive the tests.

### Go

![Desktop View](/assets/2025-06-23-Ultimate_Web_Server_Tier_List/go/photo1.png){: width="906" height="385" }
![Desktop View](/assets/2025-06-23-Ultimate_Web_Server_Tier_List/go/photo2.png){: width="905" height="392" }
![Desktop View](/assets/2025-06-23-Ultimate_Web_Server_Tier_List/go/photo3.png){: width="908" height="381" }
![Desktop View](/assets/2025-06-23-Ultimate_Web_Server_Tier_List/go/photo4.png){: width="906" height="390" }
![Desktop View](/assets/2025-06-23-Ultimate_Web_Server_Tier_List/go/photo5.png){: width="911" height="387" }

If you look at the graphs, you might see that my Go server handled a whopping **16,000,796** requests, which is even higher than Nginx! But before you get too excited, look at the HTTP failures: **800,612**. If my code didn't suck, this would have been a very different story. Still, it's impressive what Go's standard library can do out of the box.

### Rust

![Desktop View](/assets/2025-06-23-Ultimate_Web_Server_Tier_List/rust/photo1.png){: width="928" height="389" }
![Desktop View](/assets/2025-06-23-Ultimate_Web_Server_Tier_List/rust/photo2.png){: width="930" height="378" }
![Desktop View](/assets/2025-06-23-Ultimate_Web_Server_Tier_List/rust/photo3.png){: width="931" height="380" }
![Desktop View](/assets/2025-06-23-Ultimate_Web_Server_Tier_List/rust/photo4.png){: width="928" height="379" }
![Desktop View](/assets/2025-06-23-Ultimate_Web_Server_Tier_List/rust/photo5.png){: width="928" height="379" }

My Rust server didn't complete the test. At this point, I don't think my code is the _only_ problem. Maybe Rust's HTTP libraries aren't as foolproof as you'd think. (Just kidding—please don't come after me, Rustaceans. And definitely don't rewrite Nginx in Rust based on this result.)

# Last Thoughts

This experiment was great for satisfying my own curiosity. Before I ran this test, I was an Nginx-or-nothing kind of person. But now, I can see myself using `Caddy` for smaller projects.

For serious production workloads, just use `Nginx`. It's the industry standard and arguably the best all-around web server of all time for a reason.

Thanks for reading! I hope you found this nerdy deep-dive useful.
