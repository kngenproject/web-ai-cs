from flask import Flask, render_template, request, jsonify
import os
import glob
from openai import OpenAI

app = Flask(__name__)

# Mengambil API Key Nexotao dari Environment Variable Vercel / Lokal
NEXOTAO_API_KEY = os.environ.get("NEXOTAO_API_KEY", "MASUKKAN_API_KEY_NEXOTAO_DI_SINI")

# Inisialisasi Client OpenAI / Nexotao
client = None
if NEXOTAO_API_KEY and NEXOTAO_API_KEY != "MASUKKAN_API_KEY_NEXOTAO_DI_SINI":
    try:
        client = OpenAI(
            api_key=NEXOTAO_API_KEY,
            base_url="https://api.nexotao.com/v1"
        )
    except Exception as e:
        print(f"Gagal inisialisasi Nexotao: {e}")

# Jawaban Instan 0 Token untuk Sapaan Umum
QUICK_REPLIES = {
    "halo": "Halo Kak! 😊 Ada yang bisa kami bantu seputar stok buah, parcel, lokasi, atau loker di Toko Buah ABS Kepanjen?",
    "hai": "Halo Kak! 😊 Selamat datang di Toko Buah ABS Kepanjen. Ada yang bisa dibantu?",
    "hi": "Halo Kak! 😊 Ada yang bisa kami bantu hari ini?",
    "p": "Halo Kak! Ada yang bisa dibantu seputar Toko Buah ABS Kepanjen? 😊",
    "ping": "Halo Kak! Ada yang bisa dibantu? 😊",
    "terima kasih": "Sama-sama Kak! Ditunggu kedatangannya di Toko Buah ABS Kepanjen ya 😊",
    "makasih": "Sama-sama Kak! Semoga sehat selalu 😊",
    "tes": "Sistem CS AI Toko Buah ABS Kepanjen aktif dan siap membantu Kak! 😊"
}

# Fungsi Filter Dokumen Relevan (Dynamic Knowledge Retrieval)
def get_relevant_knowledge(user_msg):
    msg = user_msg.lower()
    target_files = []

    # Filter variasi kata kunci Loker / Pekerjaan
    loker_keywords = ['loker', 'kerja', 'gaji', 'syarat', 'mess', 'berkas', 'poker', 'lowongan', 'lamar', 'gawe', 'infoloker', 'ijazah', 'shift', 'jam kerja']
    if any(k in msg for k in loker_keywords):
        target_files.extend(glob.glob("knowledge/*loker*.txt"))

    # Filter variasi kata kunci Lokasi / Jam / Sosmed
    lokasi_keywords = ['alamat', 'lokasi', 'maps', 'buka', 'jam', 'instagram', 'ig', 'posisi', 'tempat', 'ancer', 'patokan', 'toko']
    if any(k in msg for k in lokasi_keywords):
        target_files.extend(glob.glob("knowledge/*lokasi*.txt"))
        target_files.extend(glob.glob("knowledge/*jam*.txt"))
        target_files.extend(glob.glob("knowledge/*sosmed*.txt"))

    # Filter variasi kata kunci Produk / Parcel / Buah
    produk_keywords = ['buah', 'parcel', 'stok', 'harga', 'parsel', 'paket', 'buah-buahan', 'ecer', 'grosir']
    if any(k in msg for k in produk_keywords):
        target_files.extend(glob.glob("knowledge/*produk*.txt"))
        target_files.extend(glob.glob("knowledge/*parcel*.txt"))

    # Hapus duplikasi nama file
    target_files = list(set(target_files))

    # Jika tidak cocok dengan kategori khusus, baca seluruh file sebagai fallback
    if not target_files:
        target_files = glob.glob("knowledge/*.txt")

    relevant_text = ""
    for fp in target_files:
        try:
            with open(fp, "r", encoding="utf-8") as f:
                relevant_text += f.read() + "\n\n"
        except Exception as e:
            print(f"Gagal membaca file {fp}: {e}")

    return relevant_text

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json() or {}
        user_msg = data.get('message', '').strip()
        
        if not user_msg:
            return jsonify({'response': 'Mohon tuliskan pertanyaan Kakak ya 😊'})

        msg_lower = user_msg.lower()

        # Balas sapaan umum secara instan (0 Token)
        if msg_lower in QUICK_REPLIES:
            return jsonify({'response': QUICK_REPLIES[msg_lower]})

        if not client:
            return jsonify({
                'response': 'Halo Kak! Sistem AI sedang dalam penyiapan (API Key Nexotao belum terpasang). Mohon hubungi admin toko ya.'
            })

        # Ambil hanya dokumen pengetahuan yang relevan dengan pertanyaan
        relevant_knowledge = get_relevant_knowledge(user_msg)

        # SYSTEM PROMPT: Menggabungkan Fleksibilitas Respon dengan Kedisiplinan Fakta Dokumen
        system_instruction = (
            "Kamu adalah Customer Service Asisten AI untuk Toko Buah ABS Kepanjen. "
            "Gaya bicaramu ramah, hangat, komunikatif, dan fleksibel seperti manusia profesional (selalu panggil 'Kak' atau 'Kak/Bunda').\n\n"
            "PANDUAN MENJAWAB KHUSUS LOKER & INFORMASI:\n"
            "1. Pahamilah pertanyaan atau maksud pelanggan meskipun ada typo, kata singkatan, atau bahasa gaul/santai.\n"
            "2. Jawablah secara FLEKSIBEL dan ALAMI. Kamu boleh menyusun kalimat penjelasan sendiri agar mudah dipahami, tetapi FAKTA DAN KETENTUAN (seperti besaran gaji, jam kerja, fasilitas mess, syarat berkas, dan kriteria) WAJIB 100% PERSIS dengan DOKUMEN PENGETAHUAN.\n"
            "3. Jika pelanggan bertanya hal spesifik tentang loker (contoh: 'ada tempat tinggalnya gak?'), jawablah poin tersebut secara langsung dan santun sesuai dokumen.\n"
            "4. Jika informasi TIDAK TERDAPAT di dokumen, katakan dengan sangat ramah bahwa informasi tersebut belum tertera di sistem dan sarankan untuk bertanya langsung saat penyerahan berkas/interview di toko.\n"
            "5. Jawab secara ringkas, informatif, dan gunakan emoji yang sesuai 😊.\n\n"
            "=== DOKUMEN PENGETAHUAN RELEVAN ===\n"
            f"{relevant_knowledge}\n"
            "==================================="
        )

        # Pemanggilan Model Nova Micro via Nexotao API
        response = client.chat.completions.create(
            model="amazon.nova-micro-v1:0",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.35, # Ditingkatkan sedikit dari 0.2 agar pilihan kata lebih bervariasi/fleksibel
            max_tokens=220    # Kuota token pas untuk penjelasan ramah
        )

        bot_reply = response.choices[0].message.content if response.choices else "Maaf Kak, AI belum bisa merespons saat ini."
        return jsonify({'response': bot_reply})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'response': f'Terjadi kendala pada sistem CS AI: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
