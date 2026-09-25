from flask import Flask, render_template, request, jsonify
import os
import glob
from openai import OpenAI

app = Flask(__name__)

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

# 1. Quick Replies 0 Token (Sapaan Umum)
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

    loker_keywords = ['loker', 'kerja', 'gaji', 'syarat', 'mess', 'berkas', 'lowongan', 'lamar', 'gawe', 'infoloker', 'ijazah', 'shift', 'jam kerja', 'cewek', 'wanita', 'perempuan']
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
        chat_history = data.get('history', [])
        
        if not user_msg:
            return jsonify({'response': 'Mohon tuliskan pertanyaan Kakak ya 😊'})

        msg_lower = user_msg.lower()

        # TEKNIK 0 TOKEN 1: Sapaan Ringan
        if msg_lower in QUICK_REPLIES:
            return jsonify({'response': QUICK_REPLIES[msg_lower]})

        # TEKNIK 0 TOKEN 2: Direct Paste Info Lengkap Loker
        full_loker_triggers = [
            'info lengkap loker', 'infoloker lengkap', 'semua info loker', 'detail loker', 
            'syarat lengkap loker', 'minta info loker', 'info loker lengkap', 'info lengkap lowongan', 
            'info lowongan', 'mana lokernya', 'dokumennya mana', 'yang mana'
        ]
        if any(trigger in msg_lower for trigger in full_loker_triggers):
            loker_files = glob.glob("knowledge/*loker*.txt")
            if loker_files:
                try:
                    with open(loker_files[0], "r", encoding="utf-8") as f:
                        loker_content = f.read().strip()
                    return jsonify({'response': f"Halo Kak! 😊 Berikut informasi lengkap lowongan pekerjaan di Toko Buah ABS Kepanjen:\n\n{loker_content}"})
                except Exception as e:
                    print(f"Gagal membaca file loker: {e}")

        if not client:
            return jsonify({
                'response': 'Halo Kak! Sistem AI sedang dalam penyiapan (API Key Nexotao belum terpasang). Mohon hubungi admin toko ya.'
            })

        combined_context = user_msg + " " + " ".join([h.get('content', '') for h in chat_history[-2:]])
        relevant_knowledge = get_relevant_knowledge(combined_context)

        system_instruction = (
            "Kamu adalah Customer Service Toko Buah ABS Kepanjen (panggil pelanggan 'Kak').\n\n"
            "PROSES BERPIKIR & CARA MENJAWAB:\n"
            "1. Pahami pertanyaan pelanggan dan hubungkan dengan riwayat percakapan sebelumnya agar nyambung.\n"
            "2. Gunakan HANYA data dari DATA TOKO di bawah.\n"
            "3. Jawab langsung inti pertanyaannya dengan jelas, sopan, dan ramah (1-3 kalimat).\n"
            "4. DILARANG KERAS menyuruh pelanggan membaca 'dokumen', 'file', atau 'sistem' di atas.\n"
            "5. Jika fakta tidak ada di data toko, sampaikan maaf secara jujur.\n\n"
            "=== DATA TOKO ABS KEPANJEN ===\n"
            f"{relevant_knowledge}\n"
            "=============================="
        )

        messages_to_ai = [{"role": "system", "content": system_instruction}]
        
        # Validasi Urutan Riwayat: Pastikan entri riwayat pertama HARUS role 'user'
        filtered_history = [h for h in chat_history[-6:] if h.get('role') in ['user', 'assistant'] and h.get('content')]
        
        # Buang pesan assistant di paling depan jika riwayat diawali oleh assistant
        while filtered_history and filtered_history[0]['role'] == 'assistant':
            filtered_history.pop(0)

        for hist in filtered_history:
            messages_to_ai.append({
                "role": hist['role'],
                "content": hist['content']
            })
        
        messages_to_ai.append({"role": "user", "content": user_msg})

        response = client.chat.completions.create(
            model="deepseek-v3-2",
            messages=messages_to_ai,
            temperature=0.3,
            max_tokens=110
        )

        bot_reply = response.choices[0].message.content if response.choices else "Maaf Kak, AI belum bisa merespons saat ini."
        return jsonify({'response': bot_reply})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'response': f'Terjadi kendala pada sistem CS AI: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
