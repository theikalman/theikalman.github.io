---
layout: post
title:  "Gagal Shutdown di Lenovo Flex 14 dengan Linux Kernel 5.3 (Ubuntu 18.04)"
date:   2020-06-01 08:15:00
categories: Troubleshot
tags:
    - Linux
    - Lenovo Flex 14
---

Setelah sekitar hampir 2 minggu yang lalu pas buka tas dan lihat laptop
masih nyala, agak heran juga karena gak biasanya linux kayak gini,
dulu pernah ngamalin (sekitar 5-6 tahun lalu) tapi itu di Windows bukan
Linux. Baru setelah satu minggu ada waktu buat start lakuin research karena
harus ngurus ini itu dulu (momen idul fitri) ketahuan lah penyebabnya
kenapa, itupun setelah 1 minggu research juga :)

Laptop Saya adalah Lenovo Flex 14. Laptop kantor sebenarnya, lol :)

Soal penyebabnya, Saya masih ragu sebenarnya, namun gambaran besarnya
adalah karena kernel Linux versi 5.3 yang sekarang nempel di Ubuntu 18.04
Saya itu ada bug yang entah bagaimana gagal membunuh semua proses yang
jalan di komputer Saya tersebut. Berikut referensi yang berkaitan dengan
masalah ini:

- [https://bugs.launchpad.net/ubuntu/+source/linux/+bug/1594023](https://bugs.launchpad.net/ubuntu/+source/linux/+bug/1594023)
- [https://askubuntu.com/questions/125844/shutdown-does-not-power-off-computer](https://askubuntu.com/questions/125844/shutdown-does-not-power-off-computer)
- [https://unix.stackexchange.com/questions/457967/shutdown-does-not-power-off-why](https://unix.stackexchange.com/questions/457967/shutdown-does-not-power-off-why)

Untuk fix, ada dua solusi yang Saya temukan dari deretan resource diatas,
nambah `acpi=force` di grub pada saat linux dijalankan, dan yang kedua
adalah upgrade kernel. Saya sudah coba yang pertama, set
`GRUB_CMDLINE_LINUX_DEFAULT` di file grub menjadi

`GRUB_CMDLINE_LINUX_DEFAULT="quiet splash acpi=force"`

dari yang asalnya

`GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"`

yang, ternyata tidak berhasil, komputer Saya tetap tidak bisa mati secara
normal. LCD screen mati, tapi backlight keyboard tetap nyala, pun tombol
power tetap mengindikasikan nyala, kipas ya juga sama masih kedengaran
tetep muter.

Solusi yang berhasil adalah yang kedua, yaitu upgrade kernel Linux, meskipun
sebenarnya agak takut juga karena takutnya malah gagal dan, ya harus benerin
dari awal. Ini bukan takut sih, tapi lebih ke males :smile: 

Saya coba lihat versi kernel Linux terakhir, ternyata yang terakhir dirilis
(versi stable) adalah `5.6.14` sementara yang terinstall di komputer Saya
adalah `5.3`. Ya sudah Saya putuskan coba install yang terakhir tersebut.

![Latest Linux Kernel Version](/postimages/2020-06-01-gagal-shutdown-lenovo-flex-ubuntu-18.04-kernel-5.3_kernel_latest_version.png)

Cara installnya Saya ikutin langkah-langkahnya sesuai yang ada di sini:

[https://www.tecmint.com/upgrade-kernel-in-ubuntu/](https://www.tecmint.com/upgrade-kernel-in-ubuntu/)

Kurang lebih download file berikut

```
linux-headers-5.6.14-050614_5.6.14-050614.202005200733_all.deb
linux-headers-5.6.14-050614-generic_5.6.14-050614.202005200733_amd64.deb
linux-image-unsigned-5.6.14-050614-generic_5.6.14-050614.202005200733_amd64.deb
linux-modules-5.6.14-050614-generic_5.6.14-050614.202005200733_amd64.deb
```

dari sini: [https://kernel.ubuntu.com/~kernel-ppa/mainline/v5.6.14/](https://kernel.ubuntu.com/~kernel-ppa/mainline/v5.6.14/)

Setelah itu install semua file tersebut dengan perintah: `sudo dpkg -i *.deb`

> Catatan:
>
> Pada saat nginstall, ada warning, kurang lebih warningnya mengatakan
> bahwa ada beberapa firmware yang hilang dibawah folder `/lib/firmware/amdgpu/`.
> Salah satu firmware yang hilang adalah `navi12_asd.bin` tapi setelah Saya coba
> cari-cari di [repo firmware linuxnya](https://git.kernel.org/pub/scm/linux/kernel/git/firmware/linux-firmware.git/tree/amdgpu)
> gak nemu, akhirnya tidak Saya hiraukan warning tersebut, walhasil tetep
> jalan kok :smile:

Dan setelah langkah tersebut, reboot komputer dan setelah nyala lagi, pastiin
kernel yang diinstall tadi sudah berhasil di load dengan command `uname -rs`,
kalo yang muncul versi `5.6.14` ya berarti berhasil. Dan di kasus Saya, berhasil.
Saya jadi bisa shutdown komputer Saya secara normal dan matinya *sangat super cepat*,
gak kayak Windows yang super lemot kalo matiin komputer. Lol.

Ok, itu saja, Saya juga udah males nulisnya, bye.
