---
layout: post
title:  "Apa Itu DevOps"
date:   2015-11-17 19:21:00
categories: DevOps
tags:
    - DevOps
    - Learning
---


Awalnya saya agak mengkerutkan dahi ketika _lead_ programmer saya bilang
"rencananya kita mau pakek __Ansible__, supaya proses _release_ jadi lebih
enteng". Segera setelah itu, (masih didepan _lead_ saya) langsung saya buka
_browser_ terus masukkin keyword "Ansible". Haha, ternyata saya baru sadar
kalo saya hidup dalam "kardus".


Gak lama kemudian _lead_ saya langsung bilang "coba kamu cari-cari tentang
DevOps". Oke, CuriousMode:On.


Saya mulai baca-baca dan, yup, sekarang mulai faham langkah-langkah bagaimana
proses dari mulai pembuatan aplikasi (coding) sampe ke tahap _packaging_
dan publishing (sekalipun cuma gambaran). Saya memang _programmer_ baru,
tepatnya baru kerja.


Jujur saja, diawal saja saya kenal [github] saya agak aneh, kenapa harus
pakai _github_? Kenapa gak _copy_-_paste_ manual aja? Memang serepot apa sih
_versioning_ (yang dulu saya menterjemahkan mentah kata ini) sampai harus
pake _tools_ macam _github_ segala? Sekarang saya mulai sadar dengan itu
semua, ya maklumlah dulu seringnya ngoding sendiri jadi ya sekarang perlahan
mulai faham apa yang membedakan antara _freelancer_ dengan
_full stack programmer_, salah satunya ya penggunaan _tools_ itu. _Freelancer_
lebih sering memilih _tools_ yang memang ya berguna buat dia (kerja sendiri)
ketimbang _full stack programmer_ yang sering kali milih _tools_ untuk
kemudahan kolaborasi. Oke stop, balik kejalur pembahasan.


Saya jadi bingung, apa hubungannya cerita diatas sama judul?


Secara tidak langsung memang agak gak nyambung (bodo amat, blog saya ini),
yang pasti, _tools_-_tools_ yang saya sebutkan diatas adalah tidak
lain salah satu dari _tools_ untuk kolaborasi dalam rangka
_software development_. Dimana sebenarnya sering kali timbul banyak masalah
ketika kita ngoding bareng-bareng, entah itu pas proses penulisan kode,
atau bahkan pada saat proses mau rilis aplikasi. Dan diartikel ini saya coba
nulis apa yang ada dikepala saya soal proses rilis, terutama _issue_ yang
sedang _"hot"_ akhir-akhir ini diproses rilis tersebut. Langsung mulai deh...


## Bagaiamana proses rilis itu?
Sebelum saya nulis soal "apa itu _DevOps_?", saya mau cerita soal bagaimana
proses rilis aplikasi itu secara garis besar (tentunya ditempat saya). Ini
penting karena nanti akan nyambung dengan judul diatas.


Yaiyalah, kalo gak nyambung ngapain ditulis, tulalit nih penulis.


Anggaplah sekarang kita sudah beres koding dengan keringat dingin mengucur
(seember -- karena _deadline_) dan kita akan merilisnya, dan biasanya
berikut ini adalah langkah-langkah yang dilakukan:

1. Mindahin _source code_ ke _server live_.
2. Melakukan beberapa konfigurasi yang dibutuhkan.


Kelihatannya _simple_ ya?


Pada kenyataanya, sebelum mindahin kodingan ke _server live_ biasanya ada
proses menjalankan semua _test_ yang ada di _source code_ tersebut. Kalo
sering ngelakuin [TDD] mungkin gak aneh yah. Kalo hasil tesnya lancar ya
lanjut, kalo ada yang 'bengkok' ya dicek ulang, dibenerin dulu.


Proses mindahin kodingan dari tempat _development_ ini juga beda-beda, tapi
kebanyakan sudah _clone_ langsung dari _repository_ ketimbang ngopi atau
ngupload kodingan secara manual lewat [FTP]. Oke, tahap ini mungkin masih
dibilang gampang--lah. Sekalipun ya ribet juga harus login ke _server_,
terus ngejalanin `git clone` atau `git pull origin master`. Belum lagi kalo
lupa naro foldernya dimana, ato lupa servernya dimana (yang ini ngarang
biar 'extreme') kan bikin repot, tapi udah terlanjur bilang gampang, ya
gampangin aja lah.


Lanjut ke proses kedua, konfigurasi. Nah ini yang agak ribet. Misal sehabis
mindahin _source code_ baru kita harus ngubah beberapa settingan kayak
_variable development_ atau ngeset server jadi mode _maintenance_ ketika
proses rilis ini, ato harus nyeting _cron job_, dll. Proses ini yang
sebenernya ribet, tapi 'kelihatan' gampang dan berulang-ulang, yang padahal
ngabisin waktu banyak, padahal misalnya hanya salah setting _cron job_, salah
masukin nama _file_ misalnya.


Dari paragrap diatas sekarang mulai ada gambaran gimana proses rilis aplikasi
dari tempat _development_ ke tempat laip (red: _live_). Dan ya agak ribet
juga, terlebih sebenarnya proses yang berulang-ulang seharusnya memang lebih
baik diotomatisasi biar meminimalisir kesalahan manusia.


## _DevOps_ itu apa?
Sekarang kita baru 'nginjek' kata ini, _DevOps_ sendiri menurut [wikipedia]
dikatakan campuran kata dari _Development_ dan _Operations_. Dimana ini
nunjukin tugas-tugas yang berkaitan dengan proses _development_ dan hal-hal
operasional lain atau staf IT lain, ya kayak situkang ngurusin _server_ yang
tugasnya ngupload _file_ kodingan kita ke _server live_ tadi itu, atau
bahkan QA (Quality Assurance) -- atau tukang tes.


### Tugas _DevOps_
Dari pengertian singkat diatas sekarang setidaknya kita tahu bahwa tugas
_DevOps_ itu ya jadi jembatan antara tukang koding, tukang tes, dan tukang
ngurus server. Kalo memang kita sering rilis secara berkala ya sebaiknya
memang _aware_ sama pentingnya _DevOps_ ini, terutama otomatisasi, karena
tentu saja kita nggak mau kalo harus melakukan tugas berulang-ulang yang
memang sebenarnya bisa diotomatisasi, yang pasti bisa menghemat waktu. Nah,
untuk beberapa _tools_ yang berkaitan dengan _DevOps_ ini ada listnya,
sebagai remainder saya juga sih, nih:

- [Jenkins]
- [Ansible]
- [Selenium]
- [Docker]
- [Bamboo]
- [Travis CI]
- dan lain-lain.


Oke, rasanya sudah capek saya nulis. Capek baca nggak? Syukurdeh (mau capek
mau enggak tetep saya sukurin, haha...).


Sekian aja dulu tulisan tentang _DevOps_, mungkin postingan selanjutnya
saya bakalan nulis tentang tutorial ato hal-hal lain yang masih berkaitan
sama _DevOps_ ini, soalnya memang lagi _curious_ banget sama yang satu ini.


See you...


[github]: https://www.github.com
[FTP]: https://en.wikipedia.org/wiki/File_Transfer_Protocol
[TDD]: https://en.wikipedia.org/wiki/Test-driven_development
[wikipedia]: https://en.wikipedia.org/wiki/DevOps
[Jenkins]: http://jenkins-ci.org/
[Ansible]: http://www.ansible.com/
[Selenium]: http://www.seleniumhq.org/
[Docker]: https://www.docker.com/
[Bamboo]: https://www.atlassian.com/software/bamboo
[Travis CI]: https://travis-ci.org/
