---
layout: post
title:  "EFS Ter-Mount dan Terbaca Tapi ECS Tidak Berhasil Menyimpan Data Ke EFS"
date:   2017-01-19 04:08:00
categories: Troubleshot
tags:
    - AWS
    - ECS
    - EFS
    - DevOps
---

Seharian kemarin, berkutat sama AWS (lagi). Ya kan emang kerjaannya pake AWS :smile:
Ada hal yang aneh ketika cluster di ECS yang sudah saya set-up agar nge-mount
EFS tidak bisa menulis ke EFS, ato singkatnya ECS tidak berhasil menulis data
ke EFS.

Tapi sebelum Saya ngasih tau alesan kenapa bisa kejadian seperti itu, dan
menceritakan bagaimana Saya nge-fix masalah tersebut, ada baiknya Saya kasih
gambaran umum dulu apa itu EFS, ECS dan AWS itu sendiri. Biar yang baca,
meski pemula gak bingung :smile:

## AWS (Amazon Web Service)
Singkatnya ini services yang ditawarkan Amazon untuk para pengembang, terutama
dilingkungan web, ya gak jauh-jauh sama cloud-computing-lah. Service yang
ditawarkan juga beragam, dari mulai VPS, AWS-Lambda (bisa jalanin kodingan
tanpa butuh server, maksudnya kita gak perlu set-up server), termasuk kalo
yang suka ngopre IoT, AWS juga nyediain yang namanya AWS IoT, dan services
yang lainnya banyak (banget), jadi gak bisa saya sebutin -- lagian gak dibayar
juga sama AWS-nya :smile:.

## ECS (EC2 Container Service)
Sebelumnya kalo belum tahu apa itu EC2, EC2 itu ya anggaplah komputer biasa
(aslinya virtual-machine). Terus, nyambungnya sama ECS apaan? ECS sendiri
sebenarnya (kalo saya bilang) service yang disediain AWS untuk manage
docker yang ada di EC2-nya itu sendiri. Apa itu docker? Kayaknya yang ini
tolong cari tahu sendiri ya :smile: ECS ini ketika kita buat instance
docker (container -- docker run kalo di lokal komputermu) akan membuat 
sendiri EC2 instance untuk nyimpen container docker-nya tersebut,
juga, kalau kita jalanin 2 atau lebih docker container ya ECS bisa kita
set supaya nambah sendiri (kalo misal kurang) EC2-nya.

## EFS (Elastic File System)
Kalo yang ini, anggaplah storage biasa, yang bisa dilepas-pasang
ke EC2 tadi itu, yang mana EC2 itu juga dipake sama ECS.

Penjelasannya singkat saja, hanya untuk memberi gambaran istilah-istilah dari
masalah yang Saya coba dokumentasikan disini. Oke, kalo gitu lanjut.

## Aku Mau Ngapain?
Niat Saya (sebenarnya kami, karena ini kerjaan kantor :smile:), adalah
karena si ECS ini sering di-restart (tiap release -- dan releasenya bisa
1-2 kali seminggu), jadi ECS gak bisa nyimpen data secara persistent, ato
tetap, jadi pas di restart ya datanya ilang, sementara data yang harus
di proses (yang sebelumnya di download dulu) itu lumayan besar, jadi
ya risih ajah harus download berulang-ulang. Jadi ya niatnya datanya
disimpen di EFS, EFSnya di mount ke ECS, nanti ECS nyimpen datanya
di EFS yang ke-mount tersebut. Singkatnya gitu.

## Konfigurasi
Konfigurasinya sebenarnya sudah berhasil ngikutin [ini](https://aws.amazon.com/blogs/compute/using-amazon-efs-to-persist-data-from-amazon-ecs-containers/).
Cuma untuk launch-configuration-nya, pake script yang sederhana, gak
seribet yang ditulis di blog tersebut, kayak gini:

```bash
#!/bin/bash

# Configure ECS cluster
echo ECS_CLUSTER=<NAMA_CLUSTER_DI_ECS> >> /etc/ecs/ecs.config

# EFS configurations
yum -y install nfs-utils
mkdir -p <PATH_FOLDER_KEMANA_EFS_TSB_AKAN_DI_MOUNT>
mount -t nfs4 -o nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2 <DISINI_DNS_EFSNYA> <PATH_FOLDER_KEMANA_EFS_TSB_AKAN_DI_MOUNT>
```

Dan ini berhasil, disebut berhasilnya gimana? Well, ngeceknya
bisa pake command `df -T`, akan keliatan apa saja yang ke mount
ke EC2 tersebut. Dan setelah coba ditulisi, berhasil juga, datanya
ke store ke EFS, begitu juga kalo EFSnya dicoba di mount dari EC2
yang lain, terbaca juga EFS beserta file yang sudah disimpan tadi.


## Masalah
Salahnya, Saya terlalu yakin kalo si ECS (docker) ini akan berhasil
nge-mount EFS (sesuai konfigurasi path diatas) ke containernya :smile:
Sampe akhirnya kejadian aneh datanya gak mau ke store di EFS.
Padahal dicek dari EC2, EFSnya sudah ke mount. Dan... dicoba ditulisi
dari container dockernya (yang dijalanin otomatis sama si ECS),
datanya kesimpen di EC2nya doang, bukan di EFS.

Iya, Saya yang salah, tolong jangan banting gelas :smile:


## Solusi
Setelah seharian berkutat, akhirnya nemu [ini](https://forums.aws.amazon.com/thread.jspa?threadID=214845)
yang cuma disuruh restart docker daemon sama agent ECSnya doang :smile:

Dicoba...

Dan yup, berhasil. Terus kalo mau otomatis gimana? Ah biasa, disimpen
di launch-configuration-nya itu loh. Tempelin script dibawah ini dipaling
bawah di script launch-configuration-nya, setelah nge-mount EFSnya:

```bash
# Restart docker daemon and ecs (docker-agent),
# so docker would be able to "see" available EFS
service docker restart && start ecs
```

Versi lengkap launch-configuration-nya:


```bash
#!/bin/bash

# Configure ECS cluster
echo ECS_CLUSTER=<NAMA_CLUSTER_DI_ECS> >> /etc/ecs/ecs.config

# EFS configurations
yum -y install nfs-utils
mkdir -p <PATH_FOLDER_KEMANA_EFS_TSB_AKAN_DI_MOUNT>
mount -t nfs4 -o nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2 <DISINI_DNS_EFSNYA> <PATH_FOLDER_KEMANA_EFS_TSB_AKAN_DI_MOUNT>

# Restart docker daemon and ecs (docker-agent),
# so docker would be able to "see" available EFS
service docker restart && start ecs
```

## Lesson Learned

### Baca dokumentasi secara seksama

Karena ternyata, di dokumentasinya ada notes, yang persis "menyinggung"
masalah ini :smile:

Dokumentasinya ada [disini](http://docs.aws.amazon.com/AmazonECS/latest/developerguide/using_data_volumes.html).
Kutipan notes-nya:

```
For operating systems that use devicemapper (such as Amazon Linux and the Amazon
ECS-optimized AMI), only file systems that are available when the Docker daemon
is started will be available to Docker containers. You can use a cloud boothook 
to mount your file system before the Docker daemon starts, or you can restart 
the Docker daemon and the Amazon ECS container agent after the file system is 
mounted to make the file system available to your container volume mounts.
```

Sekian untuk hari ini, semoga bermanfaat :thumbsup:

Dan mohon do'akan supaya Saya konsisten nulis di blog karatan ini.
