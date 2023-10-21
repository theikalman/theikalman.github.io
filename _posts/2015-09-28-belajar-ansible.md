---
layout: post
title:  "Belajar Ansible"
date:   2015-09-21 18:31:00
categories: Ansible
---


Baru denger istilah _DevOps_? _Ansible_? atau bahkan Otomatisasi _deployment_
aplikasi itu sendiri?

Okeh, sampai disini. Kita sama :smile: Berarti kita punya garis _start_ yang
sama.

Dikantor, kebetulan sedang ada _issue_ tentang _DevOps_, lebih spesifik lagi
_tools_/teknologi yang dipake adalah _Ansible_, jadinya saya penasaran dengan
teknologi ini. Jadi saya fikir, daripada saya belajar sendiri mending saya
sekalian _share_, paling tidak ini jadi catatan saya ketika saya lupa.


### Kenapa harus diotomatisasi? Manual juga masih bisa kan? Toh cuma mindahin _source code_ doang to?
Mmmm... Coba baca kebawah dulu deh :worried:

-----------------------------------------------------------------------------


## Proses _Deployment_ Aplikasi
Proses deployment aplikasi disetiap perusahaan IT memang biasanya berbeda-beda,
tergantung kebijakan dan infrastruktur yang dipilih. Namun demikian, ide dari
proses deployment tersebut 'cenderung' sama yaitu dimulai dari pemindahan
_source code_ aplikasi dari tempat _development_ ke _server live_, lalu
kemudian melakukan beberapa pengaturan yang diperlukan. Nampaknya sederhana,
tapi jika setiap 2 minggu atau 3 minggu atau berapapapun lamanya jarak
_release_ tersebut, tetap saja harus melakukan proses yang 'cenderung' berulang
dan sama (dari proses sebelumnya), apa itu efektif? Menghabiskan banyak waktu
dan tenaga untuk proses yang sama, dalam istilah _programmer_ tua itu disebut
_DRY (Do not Repeat Yourself)_. Oya, belum lagi nanti kalau misal situkang
mindahin _source code_ tersebut lupa mengkonfigurasi file anu, file ini, file
itu, apa tidak malah jadi merepotkan? Belum lagi kalau servernya banyak
gimana?


### Sebentar, lalu apa itu _DevOps_ (lebih tepatnya "siapa")?
Ok, pertanyaan ini sama juga pernah muncul dikepala saya, dari [DevOps]
sendiri kata ini terdiri dari dua suku kata yaitu _Dev_ dan _Ops_ itu sendiri.
_Dev_ untuk _Development_ (gak tahu deh, _development_ atau _developer_
:smile:) dan _Ops_ sendiri untuk _Operations_. Jadi ini gabungan dari pekerjaan
_Development_ dan _Operations_ dimana _development_ cenderung ke pembuatan,
pengembangan dan _support_ aplikasi itu sendiri sedangkan _Operations_ itu
sendiri cenderung ke pekerjaan _server administration_, _packaging_, dll.


![DevOps Intersection Image][devops-image]


_Sumber gambar:_ [Wikipedia - DevOps]


> Jika diposisikan, _DevOps_ itu berada di-irisan antara ___development___
> _(software enginereeng)_, ___Quality Assurance___ _(QA)_ dan
> ___Technology Operations___.


Untuk lebih jelasnya tentang tanggung jawab dari pekerjaan ini bisa merujuk
ke halaman [DevOps].


Sudah liat, banyak yah tanggung jawabnya. Nah justru karena itu, terkadang
proses _deployment_ jadi kelihatan ribet padahal jika di dilihat secara
secara sederhana itu hanya usaha untuk memindahkan _source code_ aplikasi dari
_development_ atau _test environment_ ke _live environment_.


Ok, sekarang saya (maksud saya pembaca) mulai faham. Lalu selanjutnya apa?

-----------------------------------------------------------------------------


## Apa Itu _Ansible_?
Saya sudah menjabarkan masalah diatas, jadi _simple_-nya ya _Ansible_ itu
membantu (atau bahkan mengganti) peran situkang _upload source code_ tadi itu.

Sudah, itu saja, kebanyakan teori malah jadi bosan nanti.

-----------------------------------------------------------------------------


## Cara Kerja _Ansible_
Mmm... Sederhana saja, saya sudah mau ke praktek ya.


Pernah pake [SSH]? Kalo belum tahu silahkan baca-baca dulu deh apa itu SSH!


_Ansible_ make SSH. Untuk proses yang lebih kompleks lagi _Ansible_ pake
_library_ [Python], tapi ya ujung-ujungnya, pake SSH itu tadi :smile:.


-----------------------------------------------------------------------------

## Praktek


### Sudah install _Ansible_?
Sebenarnya saya lupa untuk membuat postingan tentang cara instalasi _Ansible_
sendiri :smile:. Untuk sementara silahkan merujuk ke halaman dokumentasinya
[disini].


### File configurasi (default) _Ansible_.
Letak file-file configurasi _Ansible_ sebenarnya berbeda-beda, tergantung
_environment_ yang digunakan biasanya. Tapi, karena saya pake [Ubuntu], jadi
saya hanya akan menuliskan yang saya tahu saja :cry:.


Lokasi konfigurasi _Ansible_ sendiri ada di:

`/etc/ansible`

`~/.ansible`

Atau bisa langsung di dalam folder project _Ansible_ itu sendiri. Sekarang
kita akan mengintip ada apa saja difolder utama konfigurasi _Ansible_ itu
sendiri.


Kita coba ketikan perintah `ls -l /etc/ansible/` (untuk linux) dan hasil dari
eksekusi perintah tersebut seperti ini:

        ansible.cfg
        hosts


#### File `ansible.cfg`
File ini berisi konfigurasi utama _ansible_ dimana secara default, jika kita
tidak menggunakan file konfigurasi kita sendiri atau tidak mendeklarasikannya
secara langsung di _command-line_. Urutan dari file konfigurasi yang akan
digunakan oleh _ansible_ adalah


- _command line_, perintah konfigurasi yang dituliskan langsung di _terminal_
  pada saat menjalankan _ansible_.
- File konfigurasi yang diletakan pada _project ansible_ itu sendiri. Atau
  dimana direktori sekarang aktif.
- File konfigurasi yang diletakkan di directori _home_ user, di linux biasanya
  terletak di `~/.ansible`.
- Terakhir, berada di direktori utama _ansible_ itu sendiri. Di linux sendiri,
  biasanya di `/etc/ansible/`.


#### File `hosts`
File ini berisi konfigurasi _server_ yang akan kita lakukan konfigurasi. Secara
default, file ini tidak berisi apa-apa, kecuali contoh saja.


### Perintah sederhana, _Ad-Hoc command_
Sebelum kita bisa melakukan perintah sederhana ini, kita harus punya _server_
yang akan kita konfigurasi dulu, untuk demo atau praktek biasanya saya
menggunakan [VirtualBox] dan sejenisnya. Dan __pastikan sudah bisa dan sukses
login melalui SSH__. Ini karena _ansible_ menggunakan SSH, ingat tadi diatas!


Disini, saya menggunakan VirtualBox dan IP-nya saya setting static menjadi
`192.168.56.10`. Jadi saya akan mencoba mengkonfigurasi _server_ _virtual_
tersebut.


Ketikan perintah berikut di _Terminal_ (ganti `[username]` dengan _username_
masing-masing yang digunakan untuk mengakses komputer _server_):

        ansible all -u [username] --ask-pass -m ping

Perintah diatas akan melakukan _ping_ (`-m ping`) ke semua (`all`) hosts yang
kita daftarkan di file `hosts` tadi, dalam kasus ini hanya satu _server_. Dan
ingat, perintah diatas dieksekusi melalui SSH dengan _user_ (`-u [username]`)
tertentu. Dan satu lagi, `--ask-pass` saya gunakan untuk memerintahkan pada
_ansible_ agar menanyakan _password_ SSH kita ketimbang _login_ melalui
SSH key. Kedepannya saya asumsikan kita tidak perlu lagi memasukkan password
untuk SSH karena kita telah melakukan setting RSA key, jika belum, silahkan
lakukan. Tutorialnya banyak kok di [mbah].


Dan jika suskes terkoneksi ke server, responsenya harusnya seperti ini:

        192.168.56.10 | success >> {
            "changed": false,
            "ping": "pong"
        }

Tunggu dulu, perintah untuk ngeping aja kok panjang banget? Bukannya di
subjudul ditulis "perintah sederhana"?


Ya, tentu, karena kita belum melakukan konfigurasi apapun. Itu kenapa
di subjudulnya saya masukkan kata [Ad-Hoc].

-----------------------------------------------------------------------------


[DevOps]: http://devops.com/2014/01/26/defining-the-dev-and-the-ops-in-devops/
[devops-image]: https://upload.wikimedia.org/wikipedia/commons/b/b5/Devops.svg
[Wikipedia - DevOps]: https://en.wikipedia.org/wiki/DevOps
[SSH]: http://www.ssh.com/
[Python]: https://www.python.org/
[disini]: https://docs.ansible.com/ansible/intro_installation.html
[VirtualBox]: https://www.virtualbox.org/wiki/Downloads
[mbah]: https://www.google.com
[Ad-Hoc]: https://id.wikipedia.org/wiki/Ad_hoc
