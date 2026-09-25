from flask import Flask, render_template, request, jsonify
import json
import re

app = Flask(__name__)

def load_context():
    try:
        with open('context.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

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

        ctx = load_context()
        loker = ctx.get('lowongan_kerja', {})

        # 1. Pertanyaan seputar Lowongan Kerja / Loker / Syarat Kerja
        if any(w in msg for w in ['loker', 'lowongan', 'kerja', 'syarat', 'melamar', 'lamaran', 'gaji', 'karyawan', 'mess', 'mes']):
            reply = (
                f"Halo Kak! 😊 Info Lowongan Kerja di {ctx.get('nama_toko', 'Toko Buah ABS Kepanjen')}:\n\n"
                f"📌 Status: {loker.get('status', 'DIBUKA')}\n"
                f"👥 Kuota: {loker.get('kuota', '2 Karyawan Perempuan')}\n"
                f"👤 Posisi: {loker.get('posisi', 'Karyawan Toko')}\n\n"
                f"📋 Persyaratan:\n- " + "\n- ".join(loker.get('persyaratan', [])) + "\n\n"
                f"🕒 Jam Kerja: {loker.get('jam_kerja_dan_fasilitas', {}).get('jam_kerja', '07.00 - 21.00 WIB')}\n"
                f"🏠 Fasilitas: {loker.get('jam_kerja_dan_fasilitas', {}).get('fasilitas', 'Makan & minum disediakan di mess')}\n\n"
                f"📄 Berkas Lamaran:\n- " + "\n- ".join(loker.get('berkas_lamaran', [])) + "\n\n"
                f"📩 Cara Melamar: {loker.get('cara_melamar', '')}\n\n"
                f"📍 Lokasi Maps: {ctx.get('lokasi', {}).get('maps', '')}"
            )
            return jsonify({'response': reply})

        # 2. Pertanyaan seputar Jam Operasional / Buka
        elif any(w in msg for w in ['jam', 'buka', 'tutup', 'operasional', 'hari']):
            reply = f"Halo Kak! 😊 {ctx.get('nama_toko', 'Toko Buah ABS Kepanjen')} buka {ctx.get('jam_operasional', 'setiap hari pukul 08.00 - 21.00 WIB')}. Silakan mampir yaa! 🍎🍊"
            return jsonify({'response': reply})

        # 3. Pertanyaan seputar Lokasi / Alamat / Maps
        elif any(w in msg for w in ['lokasi', 'alamat', 'dimana', 'tempat', 'maps', 'peta']):
            lok = ctx.get('lokasi', {})
            reply = f"Halo Kak! 😊 {ctx.get('nama_toko')} beralamat di {lok.get('alamat', 'Kepanjen, Kabupaten Malang')}.\n\nBerikut petunjuk arah Google Maps: {lok.get('maps', '')}"
            return jsonify({'response': reply})

        # 4. Pertanyaan seputar Parcel / Buah / Produk
        elif any(w in msg for w in ['parcel', 'parsel', 'buah', 'produk', 'jual', 'stok', 'hantaran']):
            produk = ctx.get('produk_layanan', [])
            reply = f"Halo Kak! 😊 {ctx.get('nama_toko')} menyediakan:\n- " + "\n- ".join(produk) + "\n\nKakak bisa request isi parcel sesuai kebutuhan (ulang tahun, besukan, hantaran, dll). Ada yang bisa kami bantu?"
            return jsonify({'response': reply})

        # 5. Sapaan Umum
        elif any(w in msg for w in ['halo', 'hai', 'pagi', 'siang', 'sore', 'malam', 'assalamualaikum', 'permisi']):
            reply = "Halo Kak/Bunda! 😊 Selamat datang di CS Online Toko Buah ABS Kepanjen. Ada yang bisa kami bantu seputar stok buah, parcel, jam buka, lokasi, atau info lowongan kerja?"
            return jsonify({'response': reply})

        # 6. Jawaban Default jika di luar konteks
        else:
            reply = "Mohon maaf ya Kak/Bunda 😊, saat ini CS AI Toko Buah ABS Kepanjen hanya bisa membantu memberikan informasi seputar produk buah, pembuatan parcel, jam operasional, lokasi toko, dan info lowongan kerja. Ada yang ingin ditanyakan terkait hal tersebut?"
            return jsonify({'response': reply})

    except Exception as e:
        return jsonify({'response': f'Terjadi kesalahan: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
