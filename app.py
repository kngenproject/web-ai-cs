from flask import Flask, render_template, request, jsonify
import json

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

        # --- 1. GAJI, UPAH, BONUS & KEUANGAN ---
        if any(k in msg for k in ['gaji', 'upah', 'bayar', 'penghasilan', 'thr', 'bonus', 'sistem gaji', 'nominal', 'dapat berapa']):
            reply = (
                f"Halo Kak! 😊 Mengenai **gaji dan hak keuangan** di {ctx.get('nama_toko', 'Toko Buah ABS Kepanjen')}, "
                f"nominal resminya disesuaikan dengan posisi dan akan diinfokan secara transparan saat penyerahan berkas / wawancara langsung di toko yaa.\n\n"
                f"🏠 **Fasilitas Gratis:** {jam_fasilitas.get('fasilitas', 'Makan & minum disediakan bagi yang tinggal di mess')}\n"
                f"🕒 **Jam Kerja:** {jam_fasilitas.get('jam_kerja', '07.00 - 21.00 WIB')}\n\n"
                f"Yuk kirimkan CV atau langsung datang bawa lamaran ke toko! 🍎"
            )
            return jsonify({'response': reply})

        # --- 2. MESS, MAKAN, FASILITAS & TEMPAT TINGGAL ---
        elif any(k in msg for k in ['mess', 'mes', 'tinggal', 'makan', 'fasilitas', 'tidur', 'kos', 'kost', 'pp', 'pulang pergi']):
            reply = (
                f"Halo Kak! 😊 Untuk **fasilitas karyawan** di {ctx.get('nama_toko')}:\n\n"
                f"🏠 **Mess:** Disediakan bagi yang mau tinggal di tempat (gratis makan & minum).\n"
                f"🚗 **Pilihan sistem:** Boleh tinggal di mess atau PP (Pulang-Pergi).\n"
                f"⏰ **Istirahat:** Diberikan waktu istirahat 2 jam dalam sehari.\n\n"
                f"Ada yang mau ditanyakan lagi terkait fasilitasnya, Kak?"
            )
            return jsonify({'response': reply})

        # --- 3. JAM KERJA, SHIFT, LIBUR & HARI KERJA ---
        elif any(k in msg for k in ['jam', 'libur', 'shift', 'istirahat', 'sebulan', 'senin', 'minggu', 'hari kerja']):
            reply = (
                f"Halo Kak! 😊 Ketentuan **jam & hari kerja** di Toko Buah ABS:\n\n"
                f"🕒 **Jam Kerja:** {jam_fasilitas.get('jam_kerja', '±07.00 pagi - ±21.00 malam')}\n"
                f"📅 **Hari Buka:** Senin sampai Minggu (Setiap hari)\n"
                f"☕ **Istirahat:** 2 jam per hari\n"
                f"🏖 **Jatah Libur:** 2 hari dalam sebulan"
            )
            return jsonify({'response': reply})

        # --- 4. SYARAT, UMUR, KHUSUS PEREMPUAN / PRIA ---
        elif any(k in msg for k in ['syarat', 'kualifikasi', 'umur', 'usia', 'pria', 'laki', 'cewek', 'perempuan', 'ijazah', 'ktp', 'kk', 'pakaian', 'sopan']):
            syarat_list = "\n- ".join(loker.get('persyaratan', []))
            reply = (
                f"Halo Kak! 😊 Berikut adalah **persyaratan utama** melamar di {ctx.get('nama_toko')}:\n\n"
                f"👥 **Kuota Khusus:** {loker.get('kuota', '2 Karyawan Perempuan')}\n"
                f"📋 **Persyaratan:**\n- {syarat_list}\n\n"
                f"Jika memenuhi syarat di atas, Kakak bisa langsung bawa / kirimkan lamarannya yaa! 🍎"
            )
            return jsonify({'response': reply})

        # --- 5. BERKAS, CARA MELAMAR & PANGGILAN TES ---
        elif any(k in msg for k in ['berkas', 'dokumen', 'cv', 'lamaran', 'kirim', 'cara melamar', 'panggilan', 'diterima', 'wa', 'nomor']):
            berkas_list = "\n- ".join(loker.get('berkas_lamaran', []))
            reply = (
                f"Halo Kak! 😊 Berikut panduan **cara & berkas melamar**:\n\n"
                f"📄 **Berkas yang Diperlukan:**\n- {berkas_list}\n\n"
                f"📩 **Cara Kirim:**\n{loker.get('cara_melamar', '')}\n\n"
                f"⏱ **Panggilan:** {loker.get('catatan_tambahan', '')}"
            )
            return jsonify({'response': reply})

        # --- 6. LOKER UMUM / MASIH DIBUKA KAH ---
        elif any(k in msg for k in ['loker', 'lowongan', 'kerja', 'rekrutmen', 'posisi', 'tugas']):
            reply = (
                f"Halo Kak! 😊 Lowongan di {ctx.get('nama_toko')} saat ini statusnya: *{loker.get('status', 'DIBUKA')}*.\n\n"
                f"📌 **Posisi:** {loker.get('posisi', 'Karyawan Toko')}\n"
                f"👥 **Kuota:** {loker.get('kuota', '2 Karyawan Perempuan')}\n"
                f"🛠 **Tugas:** Melayani pembeli, menata dagangan, dan kegiatan terkait toko.\n\n"
                f"Kakak bisa tanyakan lebih spesifik seputar *gaji*, *mess/makan*, *jam kerja*, atau *syarat berkas* yaa!"
            )
            return jsonify({'response': reply})

        # --- 7. JAM BUKA TOKO (PELANGGAN) ---
        elif any(k in msg for k in ['buka jam', 'tutup jam', 'operasional', 'jam berapa buka']):
            reply = f"Halo Kak! 😊 {ctx.get('nama_toko')} buka {ctx.get('jam_operasional')}. Silakan mampir yaa! 🍎🍊"
            return jsonify({'response': reply})

        # --- 8. LOKASI & MAPS TOKO ---
        elif any(k in msg for k in ['lokasi', 'alamat', 'dimana', 'maps', 'peta', 'tempat']):
            alamat = lokasi.get('alamat', 'Kepanjen') if isinstance(lokasi, dict) else lokasi
            maps = lokasi.get('maps', '') if isinstance(lokasi, dict) else ''
            reply = f"Halo Kak! 😊 {ctx.get('nama_toko')} beralamat di {alamat}.\n\nGoogle Maps: {maps}"
            return jsonify({'response': reply})

        # --- 9. PARCEL & BUAH ---
        elif any(k in msg for k in ['parcel', 'parsel', 'buah', 'hantaran', 'besukan', 'stok', 'harga']):
            layanan_list = "\n- ".join(ctx.get('produk_layanan', []))
            reply = f"Halo Kak! 😊 {ctx.get('nama_toko')} menyediakan:\n- {layanan_list}\n\nBisa request isi parcel sesuai budget Kakak!"
            return jsonify({'response': reply})

        # --- 10. SAPAAN RAMAH ---
        elif any(k in msg for k in ['halo', 'hai', 'pagi', 'siang', 'sore', 'malam', 'assalamualaikum', 'permisi']):
            reply = "Halo Kak/Bunda! 😊 Selamat datang di CS Online Toko Buah ABS Kepanjen. Ada yang bisa kami bantu seputar stok buah, parcel, jam buka, lokasi, atau info lowongan kerja?"
            return jsonify({'response': reply})

        # --- 11. RESPONS JIKA TIDAK DIKENALI ---
        else:
            reply = (
                "Mohon maaf ya Kak/Bunda 😊, CS AI Toko Buah ABS Kepanjen belum memahami pertanyaan tersebut.\n\n"
                "Silakan tanyakan seputar:\n"
                "• **Info Loker** (gaji, syarat, mess, jam kerja, berkas)\n"
                "• **Layanan Toko** (stok buah, parcel, jam buka, lokasi)"
            )
            return jsonify({'response': reply})

    except Exception as e:
        return jsonify({'response': f'Terjadi kendala sistem: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
