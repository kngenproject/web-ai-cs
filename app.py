from flask import Flask, render_template, request, jsonify
import os
import glob
from openai import OpenAI

app = Flask(__name__)

# Mengambil API Key Nexotao dari Environment Variable Vercel / Lokal
NEXOTAO_API_KEY = os.environ.get("NEXOTAO_API_KEY", "MASUKKAN_API_KEY_NEXOTAO_DI_SINI")

client = None
if NEXOTAO_API_KEY and NEXOTAO_API_KEY != "MASUKKAN_API_KEY_NEXOTAO_DI_SINI":
    try:
        client = OpenAI(
            api_key=NEXOTAO_API_KEY,
            base_url="https://api.nexotao.com/v1"
        )
    except Exception as e:
        print(f"Gagal inisialisasi Nexotao: {e}")

# 1. Quick Replies 0 Token (Sapaan Langsung Dijawab Tanpa API)
QUICK_REPLIES = {
    "halo": "Halo Kak! 😊 Ada yang bisa kami bantu seputar stok buah, parcel, lokasi, atau loker di Toko Buah ABS Kepanjen?",
    "hai": "Halo Kak! 😊 Selamat datang di Toko Buah ABS Kepanjen. Ada yang bisa dibantu?",
    "hi": "Halo Kak! 😊 Ada yang bisa kami bantu hari ini?",
    "p": "Halo Kak! Ada yang bisa dibantu seputar Toko Buah ABS Kepanjen? 😊",
    "ping": "Halo Kak! Ada yang bisa dibantu? 😊",
    "selamat malam": "Selamat malam Kak! 😊 Ada yang bisa dibantu seputar Toko Buah ABS Kepanjen?",
    "selamat siang": "Selamat siang Kak! 😊 Ada yang bisa dibantu hari ini?",
    "selamat pagi": "Selamat pagi Kak! 😊 Ada yang bisa kami bantu?",
    "terima kasih": "Sama-sama Kak! Ditunggu kedatangannya di Toko Buah ABS Kepanjen ya 😊",
    "makasih": "Sama-sama Kak! Semoga sehat selalu 😊",
    "tes": "Sistem CS AI Toko Buah ABS Kepanjen aktif dan siap membantu Kak! 😊"
}

# 2. Dynamic Knowledge Retrieval
def get_relevant_knowledge(user_msg):
    msg = user_msg.lower()
    target_files = []

    loker_keywords = ['loker', 'kerja', 'gaji', 'syarat', 'mess', 'berkas', 'poker', 'lowongan', 'lamar', 'gawe', 'infoloker', 'ijazah', 'shift', 'jam kerja']
    if any(k in msg for k in loker_keywords):
        target_files.extend(glob.glob("knowledge/*loker*.txt"))

    lokasi_keywords = ['alamat', 'lokasi', 'maps', 'buka', 'jam', 'instagram', 'ig', 'posisi', 'tempat', 'ancer', 'patokan', 'toko']
    if any(k in msg for k in lokasi_keywords):
        target_files.extend(glob.glob("knowledge/*lokasi*.txt"))
        target_files.extend(glob.glob("knowledge/*jam*.txt"))
        target_files.extend(glob.glob("knowledge/*sosmed*.txt"))

    produk_keywords = ['buah', 'parcel', 'stok', 'harga', 'parsel', 'paket', 'buah-buahan', 'ecer', 'grosir', 'apel', 'jeruk', 'anggur', 'mangga']
    if any(k in msg for k in produk_keywords):
        target_files.extend(glob.glob("knowledge/*produk*.txt"))
        target_files.extend(glob.glob("knowledge/*parcel*.txt"))

    target_files = list(set(target_files))

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

        if msg_lower in QUICK_REPLIES:
            return jsonify({'response': QUICK_REPLIES[msg_lower]})

        if not client:
            return jsonify({
                'response': 'Halo Kak! Sistem AI sedang dalam penyiapan (API Key Nexotao belum terpasang). Mohon hubungi admin toko ya.'
            })

        relevant_knowledge = get_relevant_knowledge(user_msg)

        # SYSTEM PROMPT: Paling Taktis, Ramah, Solutif, dan Tidak Mengambang
        system_instruction = (
            "Kamu adalah Customer Service Asisten Toko Buah ABS Kepanjen (panggil pelanggan 'Kak').\n\n"
            "ATURAN MENJAWAB:\n"
            "1. Jawablah secara RAMAH, EMPATIS, dan NATURAL. Jangan kaku dan jangan gunakan kalimat template berulang-ulang.\n"
            "2. Gunakan FAKTA dari DOKUMEN PENGETAHUAN di bawah.\n"
            "3. Jika daftar harga/stok spesifik TIDAK TERSEDIA di dokumen, minta maaf secara sopan dan langsung berikan nomor WA Admin/Toko (jika ada di dokumen) atau sarankan untuk cek langsung saat berkunjung agar mendapat info harga harian terupdate.\n"
            "4. Jawab secara padat, jelas, tuntas, dan TIDAK TERPOTONG (maksimal 2-3 kalimat).\n\n"
            "=== DOKUMEN PENGETAHUAN ===\n"
            f"{relevant_knowledge}\n"
            "==========================="
        )

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.3,
            max_tokens=120  # Dinaikkan sedikit agar kalimat utuh dan tidak terpotong
        )

        bot_reply = response.choices[0].message.content if response.choices else "Maaf Kak, AI belum bisa merespons saat ini."
        return jsonify({'response': bot_reply})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'response': f'Terjadi kendala pada sistem CS AI: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
