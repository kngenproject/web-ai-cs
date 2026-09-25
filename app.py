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

KNOWLEDGE_CACHE = ""

def load_knowledge_base():
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

load_knowledge_base()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        load_knowledge_base() # Auto-refresh isi dokumen .txt
        data = request.get_json() or {}
        user_msg = data.get('message', '').strip()
        
        if not user_msg:
            return jsonify({'response': 'Mohon tuliskan pertanyaan Kakak ya 😊'})

        if not client:
            return jsonify({
                'response': 'Halo Kak! Sistem AI sedang dalam penyiapan (API Key Nexotao belum terpasang). Mohon hubungi admin toko ya.'
            })

        # SYSTEM PROMPT: Menginstruksikan Nova Micro untuk berpikir & patuh dokumen
        system_instruction = (
            "Kamu adalah Customer Service AI yang ramah, santun, dan cerdas dari Toko Buah ABS Kepanjen. "
            "Gunakan selalu sapaan 'Kak' atau 'Kak/Bunda'.\n\n"
            "TUGAS & ATURAN UTAMA:\n"
            "1. Pahami maksud pertanyaan pelanggan meskipun ada typo, kata singkatan, atau bahasa santai.\n"
            "2. Jawablah HANYA berdasarkan DOKUMEN PENGETAHUAN TOKO di bawah ini.\n"
            "3. Jika jawaban TIDAK ADA di dalam dokumen, katakan secara sopan bahwa informasi tersebut belum tersedia di sistem kami dan sarankan untuk bertanya langsung ke toko.\n"
            "4. Jawab secara ringkas, jelas, dan ramah tanpa mengarang informasi di luar dokumen.\n\n"
            "=== DOKUMEN PENGETAHUAN TOKO ===\n"
            f"{KNOWLEDGE_CACHE}\n"
            "================================"
        )

        # Pemanggilan Model Nova Micro via Nexotao API
        response = client.chat.completions.create(
            model="amazon.nova-micro-v1:0",  # ID Model Nova Micro di Nexotao
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.2,  # Rendah agar tidak berhalusinasi
            max_tokens=200    # Sangat hemat token output
        )

        bot_reply = response.choices[0].message.content if response.choices else "Maaf Kak, AI belum bisa merespons saat ini."
        return jsonify({'response': bot_reply})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'response': f'Terjadi kendala pada sistem CS AI: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
