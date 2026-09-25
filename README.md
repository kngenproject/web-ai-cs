# 🥭 Web AI CS - Toko Buah ABS Kepanjen

Aplikasi Customer Service AI berbasis web yang super cepat, ringan, cerdas, dan **super irit token** untuk **Toko Buah ABS Kepanjen**. Terhubung dengan API Nexotao (Model: `nova-micro`) dan siap di-deploy secara gratis di **Vercel**.

---

## ⚡ Fitur Utama & Optimasi Biaya

1. **Model Ultra Efisien (`nova-micro`)**: Menggunakan model `nova-micro` via Nexotao API untuk eksekusi reasoning cepat dan biaya terjangkau.
2. **0-Token Quick Replies**: Sapaan umum (*halo, hai, p, terima kasih, selamat malam, dll*) langsung dijawab dari memori lokal Flask tanpa memanggil API (0 Token).
3. **Dynamic Knowledge Retrieval**: Hanya membaca file `.txt` di folder `knowledge/` yang sesuai dengan topik pertanyaan pelanggan (*Loker*, *Lokasi/Jam*, *Produk/Parcel*), menghemat hingga 80% input token.
4. **Respon Ringkas & Faktual**: Dibatasi maksimal 100 token output. Menjawab dengan bahasa ramah (sapaan *Kak/Bunda*), luwes, dan 100% tersetel pada fakta dokumen `.txt`.
5. **Stateless Server Architecture**: Bebas beban riwayat obrolan di server untuk mencegah pembengkakan token secara eksponensial.

---

## 📁 Struktur Folder Proyek

```text
web-ai-cs/
├── app.py                 # Backend Flask utama (Integrasi Nexotao & Logic Caching)
├── requirements.txt       # Dependensi Python (Flask, openai)
├── vercel.json            # Konfigurasi deployment Vercel
├── README.md              # Dokumentasi proyek
├── knowledge/             # Basis Pengetahuan (.txt)
│   ├── loker.txt          # Info lowongan kerja, syarat, mess, gaji
│   ├── lokasi.txt         # Alamat toko, maps, patokan
│   ├── jam.txt            # Jam operasional toko
│   └── parcel.txt         # Info stok buah & paket parcel
├── templates/
│   └── index.html         # Tampilan UI Chat CS
└── static/                # Asset CSS/JS/Gambar (jika ada)

🚀 Panduan Deployment ke Vercel
​1. Environment Variable
​Di dashboard Vercel (Settings -> Environment Variables), tambahkan variabel berikut:
Key / Variable NameValueDescription
NEXOTAO_API_KEYsk-...API Key akun Nexotao kamu
2. Deploy via Git
​Setiap perubahan yang dipush ke branch main di GitHub akan otomatis di-build dan di-deploy oleh Vercel.
git add .
git commit -m "Update README.md sesuai arsitektur app terbaru"
git push origin main

💻 Pengujian Lokal (Termux / Laptop)
# Install dependensi
pip install -r requirements.txt

# Jalankan server Flask lokal
python app.py

Akses di browser melalui http://127.0.0.1:5000.
​Dikembangkan untuk Toko Buah ABS Kepanjen.
