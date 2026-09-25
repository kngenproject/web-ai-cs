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
        lokasi = ctx.get('lokasi', {})
        jam_fasilitas = loker.get('jam_kerja_dan_fasilitas', {})

        # --- 1. SPESIFIK LOKER: PERSYARATAN & SYARAT ---
        if any(k in msg for k in ['syarat', 'persyaratan', 'kualifikasi', 'kriteria', 'umur', 'usia', 'cewek', 'perempuan']):
            syarat_list = "\n- ".join(loker.get('persyaratan', []))
            reply = (
                f"Halo Kak! 😊 Berikut adalah persyaratan melamar kerja di {ctx.get('nama_toko', 'Toko Buah ABS Kepanjen')}:\n\n"
                f"👥 Kuota: {loker.get('kuota', '-')}\n"
                f"📋 Persyaratan:\n- {syarat_list}\n\n"
                f"Ada lagi yang ingin ditanyakan seputar berkas atau cara melamar, Kak?"
            )
            return jsonify({'response': reply})

        # --- 2. SPESIFIK LOKER: JAM KERJA, LIBUR, MESS & FASILITAS ---
        elif any(k in msg for k in ['jam kerja', 'fasilitas', 'mess', 'mes', 'makan', 'libur', 'istirahat', 'shift']):
            reply = (
                f"Halo Kak! 😊 Untuk informasi jam kerja dan fasilitas karyawan:\n\n"
                f"🕒 Jam Kerja: {jam_fasilitas.get('jam_kerja', '-')}\n"
                f"📅 Hari Kerja: {jam_fasilitas.get('hari_kerja', '-')}\n"
                f"🏠 Fasilitas: {jam_fasilitas.get('fasilitas', '-')}\n"
                f"🛠 Tugas Utama:\n- " + "\n- ".join(loker.get('tugas_pekerjaan', []))
            )
            return jsonify({'response': reply})

        # --- 3. SPESIFIK LOKER: BERKAS, CARA MELAMAR & PANGGILAN ---
        elif any(k in msg for k in ['berkas', 'cara melamar', 'kirim', 'lamaran', 'cv', 'panggilan', 'dokumen']):
            berkas_list = "\n- ".join(loker.get('berkas_lamaran', []))
            reply = (
                f"Halo Kak! 😊 Berikut berkas yang perlu disiapkan untuk melamar:\n\n"
                f"📄 Berkas Lamaran:\n- {berkas_list}\n\n"
                f"📩 Cara Melamar:\n{loker.get('cara_melamar', '')}\n\n"
                f"📌 Catatan: {loker.get('catatan_tambahan', '')}"
            )
            return jsonify({'response': reply})

        # --- 4. SPESIFIK LOKER: UMUM / STATUS LOKER ---
        elif any(k in msg for k in ['loker', 'lowongan', 'kerja', 'kerjaan', 'rekrutmen', 'lowker']):
            reply = (
                f"Halo Kak! 😊 Lowongan kerja di {ctx.get('nama_toko', 'Toko Buah ABS Kepanjen')} saat ini statusnya: *{loker.get('status', 'DIBUKA')}*.\n\n"
                f"📌 Posisi: {loker.get('posisi', '-')}\n"
                f"👥 Kuota: {loker.get('kuota', '-')}\n\n"
                f"Kakak bisa tanyakan lebih spesifik mengenai *syarat*, *berkas lamaran*, atau *jam kerja & fasilitas* yaa! 🍎"
            )
            return jsonify({'response': reply})

        # --- 5. JAM BUKA TOKO ---
        elif any(k in msg for k in ['jam buka', 'jam berapa', 'operasional', 'tutup', 'buka jam']):
            reply = f"Halo Kak! 😊 {ctx.get('nama_toko')} buka {ctx.get('jam_operasional')}. Silakan mampir yaa! 🍎🍊"
            return jsonify({'response': reply})

        # --- 6. LOKASI & ALAMAT TOKO ---
        elif any(k in msg for k in ['lokasi', 'alamat', 'dimana', 'maps', 'tempat', 'posisi toko']):
            alamat = lokasi.get('alamat', 'Kepanjen') if isinstance(lokasi, dict) else lokasi
            maps = lokasi.get('maps', '') if isinstance(lokasi, dict) else ''
            reply = f"Halo Kak! 😊 {ctx.get('nama_toko')} beralamat di {alamat}.\n\nBerikut petunjuk arah Google Maps: {maps}"
            return jsonify({'response': reply})

        # --- 7. PARCEL & BUAH ---
        elif any(k in msg for k in ['parcel', 'parsel', 'buah', 'hantaran', 'stok', 'besukan', 'ecer', 'grosir']):
            layanan_list = "\n- ".join(ctx.get('produk_layanan', []))
            reply = f"Halo Kak! 😊 {ctx.get('nama_toko')} menyediakan:\n- {layanan_list}\n\nKakak bisa request isi parcel sesuai budget dan kebutuhan!"
            return jsonify({'response': reply})

        # --- 8. SAPAAN RAMAH ---
        elif any(k in msg for k in ['halo', 'hai', 'pagi', 'siang', 'sore', 'malam', 'permisi', 'assalamualaikum']):
            reply = "Halo Kak/Bunda! 😊 Selamat datang di CS Online Toko Buah ABS Kepanjen. Ada yang bisa kami bantu seputar stok buah, pembuatan parcel, jam buka, lokasi, atau info lowongan kerja?"
            return jsonify({'response': reply})

        # --- 9. JAWABAN DEFAULT (RESPON SOPAN) ---
        else:
            reply = "Mohon maaf ya Kak/Bunda 😊, CS AI Toko Buah ABS Kepanjen belum memahami pertanyaan tersebut. Silakan tanyakan hal seputar *stok buah*, *parcel*, *jam operasional*, *lokasi toko*, atau *info lowongan kerja (loker)*."
            return jsonify({'response': reply})

    except Exception as e:
        return jsonify({'response': f'Terjadi kendala sistem: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
