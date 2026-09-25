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
            base_url="https://api.nexotao.com/v1"  # Base URL Nexotao
        )
    except Exception as e:
        print(f"Gagal inisialisasi Nexotao: {e}")

# 1. Jawaban Instan 0 Token untuk Sapaan Umum
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

# 2. Fungsi Filter Dokumen Relevan (Hemat Token)
def get_relevant_knowledge(user_msg):
    msg = user_msg.lower()
    relevant_text = ""
    target_files = []

    # Kategorisasi file berdasarkan kata kunci pertanyaan
    if any(k in msg for k in ['loker', 'kerja', 'gaji', 'syarat', 'mess', 'berkas', 'poker', 'lowongan', 'lamar']):
        target_files.extend(glob.glob("knowledge/*loker*.txt"))
    if any(k in msg for k in ['alamat', 'lokasi', 'maps', 'buka', 'jam', 'instagram', 'ig', 'posisi', 'tempat', 'ancer']):
        target_files.extend(glob.glob("knowledge/*lokasi*.txt"))
        target_files.extend(glob.glob("knowledge/*jam*.txt"))
        target_files.extend(glob.glob("knowledge/*sosmed*.txt"))
    if any(k in msg for k in ['buah', 'parcel', 'stok', 'harga', 'parsel', 'paket', 'buah-buahan']):
        target_files.extend(glob.glob("knowledge/*produk*.txt"))
        target_files.extend(glob.glob("knowledge/*parcel*.txt"))

    # Hapus duplikasi nama file
    target_files = list(set(target_files))

    # Jika tidak cocok dengan kategori khusus, baca seluruh file sebagai fallback
    if not target_files:
        target_files = glob.glob("knowledge/*.txt")

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

        # TEKNIK HEMAT 1: Balas sapaan umum secara instan (0 Token)
        if msg_lower in QUICK_REPLIES:
            return jsonify({'response': QUICK_REPLIES[msg_lower]})

        if not client:
            return jsonify({
                'response': 'Halo Kak! Sistem AI sedang dalam penyiapan (API Key Nexotao belum terpasang). Mohon hubungi admin toko ya.'
            })

        # TEKNIK HEMAT 2: Hanya ambil dokumen pengetahuan yang relevan dengan pertanyaan
        relevant_knowledge = get_relevant_knowledge(user_msg)

        # SYSTEM PROMPT: Menginstruksikan Nova Micro untuk berpikir & patuh dokumen
        system_instruction = (
            "Kamu adalah Customer Service AI yang ramah, santun, dan cerdas dari Toko Buah ABS Kepanjen. "
            "Gunakan selalu sapaan 'Kak' atau 'Kak/Bunda'.\n\n"
            "TUGAS & ATURAN UTAMA:\n"
            "1. Pahami maksud pertanyaan pelanggan meskipun ada typo, kata singkatan, atau bahasa santai.\n"
            "2. Jawablah HANYA berdasarkan DOKUMEN PENGETAHUAN TOKO di bawah ini.\n"
            "3. Jika jawaban TIDAK ADA di dalam dokumen, katakan secara sopan bahwa informasi tersebut belum tersedia di sistem kami dan sarankan untuk bertanya langsung ke toko.\n"
            "4. Jawab secara ringkas, padat, dan ramah tanpa mengarang informasi di luar dokumen.\n\n"
            "=== DOKUMEN PENGETAHUAN RELEVAN ===\n"
            f"{relevant_knowledge}\n"
            "==================================="
        )

        # Pemanggilan Model Nova Micro via Nexotao API
        response = client.chat.completions.create(
            model="amazon.nova-micro-v1:0",  # ID Model Nova Micro di Nexotao
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.2,  # Rendah agar tidak berhalusinasi
            max_tokens=180    # Dibatasi agar balasan ringkas & sangat hemat token
        )

        bot_reply = response.choices[0].message.content if response.choices else "Maaf Kak, AI belum bisa merespons saat ini."
        return jsonify({'response': bot_reply})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'response': f'Terjadi kendala pada sistem CS AI: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
