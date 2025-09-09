# 🐾 Pet Shop Discord Bot

Pet Shop Bot adalah bot Discord sederhana yang dibuat untuk membantu **klinik hewan / pet shop** berinteraksi dengan pelanggan secara lebih cepat dan interaktif.  
Bot ini dapat menjawab pertanyaan umum seperti jam operasional, dokter yang sedang bertugas, alamat klinik, hingga produk yang tersedia.  

---

## 📌 Latar Belakang

Di era digital, banyak pemilik hewan peliharaan yang mencari informasi cepat tanpa harus datang langsung ke klinik.  
Namun, tidak semua klinik memiliki customer service yang siap 24 jam.  
**Solusinya?** Sebuah **Discord bot** yang bisa menjawab pertanyaan dasar secara otomatis.  

Bot ini dibuat dengan tujuan:
- Membantu pelanggan mendapat informasi dengan cepat.
- Mengurangi beban staf klinik untuk menjawab pertanyaan yang berulang.
- Menjadi sarana interaktif yang lebih ramah untuk komunitas pecinta hewan.

---

## ⚙️ Fitur

✅ Jawaban otomatis untuk pertanyaan umum:
- Jam operasional  
- Dokter hewan yang sedang bertugas  
- Alamat klinik  
- Produk yang tersedia di pet shop  
- Sapaan ramah untuk pengunjung baru  

✅ **Fallback Response**  
Jika bot tidak mengenali pertanyaan, bot akan memberikan jawaban default yang mengarahkan pengguna ke opsi pertanyaan yang valid.  

✅ **Integrasi MongoDB**  
Menyimpan data jadwal dokter, jam operasional, dan pengaturan lain agar mudah diperbarui tanpa perlu mengubah kode.  

✅ **Logging**  
Setiap interaksi pengguna dengan bot terekam ke dalam file `logs/bot.log` untuk mempermudah debugging dan monitoring.  

---

## 🛠️ Tech Stack

- [Python 3.10+](https://www.python.org/)  
- [discord.py](https://github.com/Rapptz/discord.py)  
- [motor](https://motor.readthedocs.io/) (MongoDB Async Driver)  
- [python-dotenv](https://pypi.org/project/python-dotenv/)  
- [logging](https://docs.python.org/3/library/logging.html)  

---

## 📖 Contoh Penggunaan

Di dalam server Discord:

User: hello
Bot : Hello there! I'm the Pet Shop bot. How can I help you today?

User: what are your hours?
Bot : We are open from 9:00 AM to 6:00 PM, Monday to Saturday. We are closed on Sundays.

## 🤝 Kontribusi

Pull request selalu diterima!
Jika ingin menambahkan fitur baru seperti booking janji temu online atau notifikasi vaksinasi, silakan buat issue atau langsung PR ke branch development.

## 📜 Lisensi

MIAWDUWA License © 2025
Kamu bebas menggunakan, mengubah, dan mendistribusikan bot ini untuk keperluan pribadi maupun komersial.

## ✨ Dibuat dengan ❤️ untuk semua pecinta hewan.
