---
layout: post
title:  "TIL: Cache Busting in Flutter"
date:   2026-08-25 00:00:01
categories: Learning
tags:
    - Learning
    - TIL
    - Flutter
    - Development
---

Recently, I found myself in a situation where I was stuck in the past, No, I
mean my Flutter Web app is not up-to-date, and I have to clear the browser
cache to get it to get the latest changes.

### The "Cache Guarding a Cache" Paradox

I found [this article](https://dev.to/adriengras/please-clear-your-cache-how-i-finally-fixed-flutter-web-caching-for-good-5dlj)
by Adrien Gras, explaining the problem well about the cache guarding a cache in
Flutter case.

Flutter Web caching is uniquely painful because of the relationship between the
entry point and the service worker. Adrien Gras highlights this specific file
chain as the root of the failure:

"The browser caches index.html, which contains references to all other files.
If the browser serves a stale index.html, it loads stale references... The
service worker makes it worse. Once installed, [it] aggressively caches
everything... It’s a cache guarding a cache." - Adrien Gras

The browser protects the index.html, which points to a stale
flutter_service_worker.js, which then intercepts and serves stale assets from
the local Cache API. It is a closed loop of obsolescence.

### The Solution I Take

There are several options that I can take to solve this problem:
1. Disable PWA completely
2. Path-based versioning
3. The `sw` dart package

I would not explain each detail of the solution here as this is
just a "devlog".

I choose to go with the `sw` package, which is a replacement of the
flutter's service worker itself. Reason is that the app still needs
to be published to web, android and ios which is not possible with
solution 1, also I don't wanna go into a hustle of setting up a
dedicated directory for the assets (which is solution 2), so I'm
going with the `sw` package.

Yeah, so that is my journey with Flutter so far. I am not a big fan
of flutter or frontend in general tbh, but I use it on my work place.
And for web app that needs to be published to web, android and ios,
flutter excels in this area.

