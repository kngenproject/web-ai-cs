from flask import Flask, render_template, request, jsonify
import os
import glob

app = Flask(__name__)

# =========================================================
# GLOBAL CACHING: Membaca pengetahuan HANYA SEKALI di RAM
# =========================================================
KNOWLEDGE_CACHE = ""
RESPONSE_CACHE = {}

def init_knowledge_base():
    global KNOWLEDGE_CACHE
    combined_text = ""
    txt_files = glob.glob("knowledge/*.txt")
    for filepath in txt_files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                combined_text += f.read() + "\n\n"
        except Exception as e:
            print(f"Gagal membaca file {filepath}: {e}")
    KNOWLEDGE_CACHE = combined_text
    print(f"✅ Knowledge Base berhasil dimuat ke RAM ({len(txt_files)} file .txt).")

init_knowledge_base()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json() or {}
        msg = data.get('message', '').lower().strip()
        
        if not msg:
            return jsonify({'response': 'Mohon tuliskan pertanyaan Kakak ya 😊'})

        if msg in RESPONSE_CACHE:
            return jsonify({'response': RESPONSE_CACHE[msg]})

        reply = ""

        # Instagram & Sosial Media
        if any(k in msg for k in ['instagram', 'ig', 'sosmed', 'sosial media', 'media sosial', 'abskepanjen']):
            reply = (
                "Halo Kak! 😊 Silakan ikuti akun Instagram resmi Toko Buah ABS Kepanjen di **@abskepanjen** "
                "untuk update stok buah segar, contoh parcel, dan promo menarik!\n\n"
                "📸 **Instagram:** https://www.instagram.com/abskepanjen/"
            )

        # Gaji & Upah
        elif any(k in msg for k in ['gaji', 'upah', 'bayar', 'penghasilan', 'thr', 'bonus', 'dapat berapa']):
            reply = (
                "Halo Kak! 😊 Mengenai **gaji dan hak keuangan** di Toko Buah ABS Kepanjen, "
                "nominal resminya disesuaikan dengan posisi dan disampaikan secara transparan saat wawancara / penyerahan berkas langsung di toko yaa.\n\n"
                "🏠 **Fasilitas:** Makan & minum disediakan bagi yang tinggal di mess.\n"
                "🕒 **Jam Kerja:** ±07.00 - ±21.00 WIB (Libur 2 hari/bulan, istirahat 2 jam/hari).\n\n"
                "Yuk kirimkan CV atau langsung datang ke toko! 🍎"
            )

        # Mess & Fasilitas
        elif any(k in msg for k in ['mess', 'mes', 'tinggal', 'makan', 'fasilitas', 'tidur', 'kos', 'kost', 'pp']):
            reply = (
                "Halo Kak! 😊 Untuk **fasilitas karyawan** di Toko Buah ABS:\n\n"
                "🏠 **Mess:** Disediakan gratis bagi yang mau tinggal di tempat (termasuk makan & minum).\n"
                "🚗 **Sistem Kerja:** Boleh tinggal di mess atau PP (Pulang-Pergi).\n"
                "☕ **Istirahat:** 2 jam per hari."
            )

        # Jam Kerja & Libur
        elif any(k in msg for k in ['jam kerja', 'shift', 'libur', 'istirahat', 'sebulan', 'hari kerja']):
            reply = (
                "Halo Kak! 😊 Ketentuan **jam & hari kerja** di Toko Buah ABS:\n\n"
                "🕒 **Jam Kerja:** ±07.00 - ±21.00 WIB\n"
                "📅 **Hari Kerja:** Senin - Minggu (Toko buka setiap hari)\n"
                "☕ **Istirahat:** 2 jam sehari\n"
                "🏖 **Libur:** 2 hari dalam sebulan"
            )

        # Syarat Loker
        elif any(k in msg for k in ['syarat', 'kualifikasi', 'umur', 'usia', 'pria', 'laki', 'cewek', 'perempuan', 'ijazah']):
            reply = (
                "Halo Kak! 😊 **Persyaratan melamar** di Toko Buah ABS Kepanjen:\n\n"
                "👥 **Kuota:** 2 Karyawan Perempuan\n"
                "📋 **Syarat:** Memiliki KTP/KK, niat kerja, berpenampilan sopan, maksimal usia ±25 tahun.\n"
                "🏠 Boleh tinggal di mess atau PP (Pulang-Pergi)."
            )

        # Berkas & Cara Melamar
        elif any(k in msg for k in ['berkas', 'dokumen', 'cv', 'lamaran', 'kirim', 'cara melamar', 'panggilan']):
            reply = (
                "Halo Kak! 😊 Panduan **berkas & cara melamar**:\n\n"
                "📄 **Berkas Required:** Foto & data diri, riwayat pendidikan, pengalaman kerja (jika ada), Fc KTP/KK, Fc Ijazah terakhir.\n\n"
                "📩 **Cara Kirim:** Kirim softfile via WA atau antar langsung ke Toko Buah ABS Kepanjen.\n"
                "📍 **Lokasi Maps:** https://goo.gl/maps/sDB87wgjQrQ2\n"
                "⏱ **Catatan:** Jika dalam 1-2 hari belum ada panggilan setelah kirim berkas, mohon maaf kemungkinan belum diterima."
            )

        # Loker Umum
        elif any(k in msg for k in ['loker', 'lowongan', 'kerja', 'rekrutmen', 'posisi']):
            reply = (
                "Halo Kak! 😊 Lowongan di Toko Buah ABS Kepanjen saat ini statusnya: **DIBUKA KEMBALI**.\n\n"
                "📌 **Posisi:** Karyawan Toko / Pramuniaga\n"
                "👥 **Kuota:** 2 Karyawan Perempuan (Max usia ±25 tahun)\n"
                "🛠 **Tugas:** Melayani pembeli, menata dagangan, dan kegiatan terkait toko.\n\n"
                "Tanyakan spesifik seputar *gaji*, *mess*, *jam kerja*, atau *syarat berkas* yaa!"
            )

        # Jam Buka Toko
        elif any(k in msg for k in ['buka', 'tutup', 'jam berapa', 'operasional']):
            reply = "Halo Kak! 😊 Toko Buah ABS Kepanjen buka setiap hari pukul 08.00 - 21.00 WIB. Silakan mampir! 🍎🍊"

        # Lokasi Toko
        elif any(k in msg for k in ['lokasi', 'alamat', 'dimana', 'maps', 'tempat', 'peta', 'petunjuk']):
            reply = (
                "Halo Kak! 😊 Toko Buah ABS beralamat di Kepanjen, Kabupaten Malang.\n\n"
                "📍 **Google Maps:** https://goo.gl/maps/sDB87wgjQrQ2\n"
                "📸 **Instagram:** https://www.instagram.com/abskepanjen/"
            )

        # Parcel & Buah
        elif any(k in msg for k in ['parcel', 'parsel', 'buah', 'hantaran', 'besukan', 'stok']):
            reply = "Halo Kak! 😊 Toko Buah ABS menyediakan buah lokal & import segar serta melayani pembuatan Parcel Buah Custom (Ulang Tahun, Besukan, Hantaran, dll)."

        # Sapaan
        elif any(k in msg for k in ['halo', 'hai', 'pagi', 'siang', 'sore', 'malam', 'assalamualaikum', 'permisi']):
            reply = "Halo Kak/Bunda! 😊 Selamat datang di CS Online Toko Buah ABS Kepanjen. Ada yang bisa kami bantu seputar stok buah, parcel, jam buka, lokasi, Instagram, atau info lowongan kerja?"

        # Fallback Search di RAM
        else:
            for line in KNOWLEDGE_CACHE.split('\n'):
                if any(word in line.lower() for word in msg.split() if len(word) > 3):
                    reply = f"Halo Kak! 😊 Berdasarkan catatan informasi toko:\n\n\"{line.strip()}\""
                    break
            if not reply:
                reply = (
                    "Mohon maaf ya Kak/Bunda 😊, CS AI Toko Buah ABS Kepanjen belum menemukan informasi tersebut.\n\n"
                    "Silakan tanyakan seputar:\n"
                    "• **Info Loker** (gaji, syarat, mess, jam kerja, berkas)\n"
                    "• **Layanan & Sosmed** (stok buah, parcel, jam buka, lokasi, Instagram)"
                )

        RESPONSE_CACHE[msg] = reply
        return jsonify({'response': reply})

    except Exception as e:
        return jsonify({'response': f'Terjadi kendala sistem: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
