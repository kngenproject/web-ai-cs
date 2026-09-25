# Web AI CS - Toko Buah ABS Kepanjen

Aplikasi layanan pelanggan (Customer Service) dan informasi rekrutmen (Loker) berbasis AI otomatis menggunakan Flask dan API `nova-micro` (Nexotao) yang dioptimalkan untuk efisiensi token.

## Fitur Utama
- **Customer Service AI**: Menjawab pertanyaan umum seputar jam buka, lokasi, dan stok buah.
- **Modul Rekrutmen (Loker)**: Membantu pelamar kerja mendapatkan informasi lowongan pekerjaan dan kualifikasi yang dibutuhkan.
- **Panel Admin**: Antarmuka untuk mengelola dan memperbarui konteks bisnis (`context.json`).
- **Efisiensi Token**: Menggunakan batasan `max_tokens` untuk menekan biaya operasional API.

## Struktur Proyek

web-ai-cs/
├── app.py              # Server Flask & integrasi API AI
├── context.json        # Basis data pengetahuan bisnis & loker
├── requirements.txt   # Dependensi Python
├── render.yaml         # Konfigurasi deployment Render
├── templates/
│   ├── index.html      # Tampilan antarmuka chat CS
│   └── admin.html      # Tampilan panel pengelolaan admin
└── README.md           # Dokumentasi proyek
## Jalankan Secara Lokal
```bash
# Install dependensi
pip install -r requirements.txt

# Jalankan aplikasi
python app.py
Akses di browser melalui http://localhost:5000.
​Deployment
​Aplikasi ini dikonfigurasi untuk siap di-deploy di platform Render.com.
