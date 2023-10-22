---
layout: post
title:  "Setting Touch-Pad di Elementary OS Freya"
date:   2015-12-13 02:44:00
categories: Troubleshot
tags:
    - Linux
    - Troubleshot
---

Kebetulan 2 minggu yang lalu saya beli laptop baru dan... ya biasa, instalasi
dan ya gitu, melakukan beberapa setting supaya lebih 'gue banget'. Kebetulan
juga (banyak kebetulannya) saya liat video macbook yang 'nggeser workspacenya
enak banget pake 4 jari, srettt... Walhasil, sayapun jadi _kabita_ dan
langsung nyari-nyari tools apa yang bisa saya pake.


Okeh, akhirnya ada beberapa tools yang ternyata bisa saya gunakan untuk
memaksimalkan kemampuan touch-pad saya tersebut, setelah sebelumnya cuma
dipake buat scroll atas bawah pakek dua jari doang :smile:


Tools yang bisa dipake bisa macem-macem, dan ternyata secara bawaan di
elementary os juga ternyata sudah ada, yaitu [ginn] dan setelah saya
coba-coba browsing dan coba melakukan beberapa konfigurasi dengan hasil
hampir 70% touch-pad saya tidak bekerja dengan baik. Sebenarnya sama ginnya
(touch-pad saya kedetect) hanya saja entah kenapa [ginn] gak ngejalanin
perintahnya. Terus saya coba-coba install aplikasi lain, dan nemulah
[touchegg]. Awalnya agak ragu juga, soalnya direpositorynya sendiri
update-an terakhir adalah 2 tahun lalu, sedangkan saya baru aja beli
laptop 2 minggu yang lalu, bisa saja hardware saya tidak compatible,
fikir saya. Tapi setelah saya coba akhirnya justru malah hasilnya lebih baik,
dan langsung ajah saya coba cari-cari konfigurasi yang orang lain pakek buat
aplikasi ini, dan akhirnya nemu juga. Saya lupa dari mana sumbernya :smile:
tapi mudah-mudahan 'mpunya' gak ngamuk :smile: dan saya backup langsung di
[gists] saya, supaya nanti saya bisa pakek lagi kalo suatu saat saya install
ulang lagi.


Oke, berikut ini step buat masang [touchegg] di elementary os:


1. Install [touchegg] dengan command: `sudo apt-get install touchegg` atau build
   langsung dari source codenya.
2. Tambahkan file konfigurasinya, kopi dari [sini], dan simpan di
   `~/.config/touchegg/touchegg.conf`
3. Tambahkan [touchegg] agar dijalankan pas start-up, caranya ada di
   _System Settings_ dibagian _Applications_ dan di tab _Startup_ dan klik
   tanda plus (+) di bagian kiri bawah dan tuliskan `/usr/bin/touchegg` lalu
   tekan enter.
4. Selesai, coba logout dan login lagi. Terus coba geser workspace dengan 4
   jari (kekiri atau kekanan). Atau expands workspace dengan slide 4 jari
   kearah atas.


Itu ajah. Untuk distro linux yang lain mungkin tidak terlalu jauh berbeda
:smile:


[touchegg]: https://github.com/JoseExposito/touchegg
[ginn]: https://launchpad.net/canonical-multitouch/ginn
[sini]: https://gist.github.com/ajiyakin/5a7254158852cbe901ce
[gists]: https://gist.github.com/ajiyakin/5a7254158852cbe901ce
