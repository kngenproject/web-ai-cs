from flask import Flask, render_template, request, jsonify
import os
import glob

app = Flask(__name__)

def load_all_knowledge():
    """Membaca seluruh isi file .txt di folder knowledge/"""
    combined_text = ""
    txt_files = glob.glob("knowledge/*.txt")
    for filepath in txt_files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                combined_text += f.read() + "\n\n"
        except Exception as e:
            print(f"Gagal membaca file {filepath}: {e}")
    return combined_text.lower(), combined_text

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

        knowledge_lower, knowledge_raw = load_all_knowledge()

        # 1. Pertanyaan seputar Gaji / Upah
        if any(k in msg for k in ['gaji', 'upah', 'bayar', 'penghasilan', 'thr', 'bonus', 'dapat berapa']):
            reply = (
                "Halo Kak! 😊 Mengenai **gaji dan hak keuangan** di Toko Buah ABS Kepanjen, "
                "nominal resminya disesuaikan dengan posisi dan disampaikan secara transparan saat wawancara / penyerahan berkas langsung di toko yaa.\n\n"
                "🏠 **Fasilitas:** Makan & minum disediakan bagi yang tinggal di mess.\n"
                "🕒 **Jam Kerja:** ±07.00 - ±21.00 WIB (Libur 2 hari/bulan, istirahat 2 jam/hari).\n\n"
                "Yuk kirimkan CV atau langsung datang ke toko! 🍎"
            )
            return jsonify({'response': reply})

        # 2. Pertanyaan Mess / Makan / Tempat Tinggal
        elif any(k in msg for k in ['mess', 'mes', 'tinggal', 'makan', 'fasilitas', 'tidur', 'kos', 'kost', 'pp']):
            reply = (
                "Halo Kak! 😊 Untuk **fasilitas karyawan** di Toko Buah ABS:\n\n"
                "🏠 **Mess:** Disediakan gratis bagi yang mau tinggal di tempat (termasuk makan & minum).\n"
                "🚗 **Sistem Kerja:** Boleh tinggal di mess atau PP (Pulang-Pergi).\n"
                "☕ **Istirahat:** 2 jam per hari."
            )
            return jsonify({'response': reply})

        # 3. Pertanyaan Jam Kerja & Libur
        elif any(k in msg for k in ['jam kerja', 'shift', 'libur', 'istirahat', 'sebulan', 'hari kerja']):
            reply = (
                "Halo Kak! 😊 Ketentuan **jam & hari kerja** di Toko Buah ABS:\n\n"
                "🕒 **Jam Kerja:** ±07.00 - ±21.00 WIB\n"
                "📅 **Hari Kerja:** Senin - Minggu (Toko buka setiap hari)\n"
                "☕ **Istirahat:** 2 jam sehari\n"
                "🏖 **Libur:** 2 hari dalam sebulan"
            )
            return jsonify({'response': reply})

        # 4. Syarat / Kualifikasi Melamar
        elif any(k in msg for k in ['syarat', 'kualifikasi', 'umur', 'usia', 'pria', 'laki', 'cewek', 'perempuan', 'ijazah']):
            reply = (
                "Halo Kak! 😊 **Persyaratan melamar** di Toko Buah ABS Kepanjen:\n\n"
                "👥 **Kuota:** 2 Karyawan Perempuan\n"
                "📋 **Syarat:** Memiliki KTP/KK, niat kerja, berpenampilan sopan, maksimal usia ±25 tahun.\n"
                "🏠 Boleh tinggal di mess atau PP (Pulang-Pergi)."
            )
            return jsonify({'response': reply})

        # 5. Berkas & Cara Melamar
        elif any(k in msg for k in ['berkas', 'dokumen', 'cv', 'lamaran', 'kirim', 'cara melamar', 'panggilan']):
            reply = (
                "Halo Kak! 😊 Panduan **berkas & cara melamar**:\n\n"
                "📄 **Berkas Required:** Foto & data diri, riwayat pendidikan, pengalaman kerja (jika ada), Fc KTP/KK, Fc Ijazah terakhir.\n\n"
                "📩 **Cara Kirim:** Kirim softfile via WA atau antar langsung ke Toko Buah ABS Kepanjen.\n"
                "📍 **Lokasi Maps:** https://goo.gl/maps/sDB87wgjQrQ2\n"
                "⏱ **Catatan:** Jika dalam 1-2 hari belum ada panggilan setelah kirim berkas, mohon maaf kemungkinan belum diterima."
            )
            return jsonify({'response': reply})

        # 6. Informasi Loker Umum
        elif any(k in msg for k in ['loker', 'lowongan', 'kerja', 'rekrutmen', 'posisi']):
            reply = (
                "Halo Kak! 😊 Lowongan di Toko Buah ABS Kepanjen saat ini statusnya: **DIBUKA KEMBALI**.\n\n"
                "📌 **Posisi:** Karyawan Toko / Pramuniaga\n"
                "👥 **Kuota:** 2 Karyawan Perempuan (Max usia ±25 tahun)\n"
                "🛠 **Tugas:** Melayani pembeli, menata dagangan, dan kegiatan terkait toko.\n\n"
                "Tanyakan spesifik seputar *gaji*, *mess*, *jam kerja*, atau *syarat berkas* yaa!"
            )
            return jsonify({'response': reply})

        # 7. Informasi Toko (Jam Buka, Lokasi, Parcel)
        elif any(k in msg for k in ['buka', 'tutup', 'jam berapa', 'operasional']):
            reply = "Halo Kak! 😊 Toko Buah ABS Kepanjen buka setiap hari pukul 08.00 - 21.00 WIB. Silakan mampir! 🍎🍊"
            return jsonify({'response': reply})

        elif any(k in msg for k in ['lokasi', 'alamat', 'dimana', 'maps', 'tempat']):
            reply = "Halo Kak! 😊 Toko Buah ABS beralamat di Kepanjen, Kabupaten Malang.\n\nGoogle Maps: https://goo.gl/maps/sDB87wgjQrQ2"
            return jsonify({'response': reply})

        elif any(k in msg for k in ['parcel', 'parsel', 'buah', 'hantaran', 'besukan', 'stok']):
            reply = "Halo Kak! 😊 Toko Buah ABS menyediakan buah lokal & import segar serta melayani pembuatan Parcel Buah Custom (Ulang Tahun, Besukan, Hantaran, dll)."
            return jsonify({'response': reply})

        elif any(k in msg for k in ['halo', 'hai', 'pagi', 'siang', 'sore', 'malam', 'assalamualaikum', 'permisi']):
            reply = "Halo Kak/Bunda! 😊 Selamat datang di CS Online Toko Buah ABS Kepanjen. Ada yang bisa kami bantu seputar stok buah, parcel, jam buka, lokasi, atau info lowongan kerja?"
            return jsonify({'response': reply})

        # 8. Pencocokan Otomatis dari Isi File .TXT (Pencarian Teks Fleksibel)
        else:
            # Mencari kalimat di file .txt yang relevan dengan pertanyaan
            for line in knowledge_raw.split('\n'):
                if any(word in line.lower() for word in msg.split() if len(word) > 3):
                    return jsonify({'response': f"Halo Kak! 😊 Berdasarkan catatan informasi toko:\n\n\"{line.strip()}\""})

            reply = (
                "Mohon maaf ya Kak/Bunda 😊, CS AI Toko Buah ABS Kepanjen belum menemukan informasi tersebut.\n\n"
                "Silakan tanyakan seputar:\n"
                "• **Info Loker** (gaji, syarat, mess, jam kerja, berkas)\n"
                "• **Layanan Toko** (stok buah, parcel, jam buka, lokasi)"
            )
            return jsonify({'response': reply})

    except Exception as e:
        return jsonify({'response': f'Terjadi kendala sistem: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
