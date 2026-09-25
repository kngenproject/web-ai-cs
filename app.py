from flask import Flask, render_template, request, jsonify
import os
import glob
from openai import OpenAI

app = Flask(__name__)

# Masukkan API Key Nexotao kamu di sini atau set via Environment Variable
NEXOTAO_API_KEY = os.environ.get("NEXOTAO_API_KEY", "MASUKKAN_API_KEY_NEXOTAO_DI_SINI")

# Inisialisasi Client OpenAI / Nexotao
client = None
if NEXOTAO_API_KEY and NEXOTAO_API_KEY != "MASUKKAN_API_KEY_NEXOTAO_DI_SINI":
    try:
        client = OpenAI(
            api_key=NEXOTAO_API_KEY,
            base_url="https://api.nexotao.com/v1"  # URL Endpoint Nexotao
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
        load_knowledge_base() # Membaca ulang isi file .txt jika ada perubahan
        data = request.get_json() or {}
        user_msg = data.get('message', '').strip()
        
        if not user_msg:
            return jsonify({'response': 'Mohon tuliskan pertanyaan Kakak ya 😊'})

        if not client:
            return jsonify({
                'response': 'Halo Kak! Sistem AI sedang dalam penyiapan (API Key Nexotao belum terpasang). Mohon hubungi admin toko ya.'
            })

        # SYSTEM PROMPT: Memaksa AI berpikir HANYA berpatokan pada dokumen toko
        system_instruction = (
            "Kamu adalah Customer Service Asisten AI ramah dari Toko Buah ABS Kepanjen. "
            "Tugasmu adalah menjawab pertanyaan pelanggan dengan sopan, hangat, dan membantu. "
            "Gunakan selalu sapaan seperti 'Kak' atau 'Kak/Bunda'.\n\n"
            "ATURAN MUTLAK JAWABAN:\n"
            "1. Jawablah pertanyaan HANYA berdasarkan DOKUMEN PENGETAHUAN TOKO di bawah ini.\n"
            "2. Jangan pernah mengarang, meniru, atau memperkirakan informasi yang tidak tertulis di dokumen.\n"
            "3. Jika pertanyaan pelanggan TIDAK ADA informasinya di dalam dokumen, katakan dengan sangat ramah bahwa informasi tersebut belum tersedia di sistem kami dan sarankan untuk bertanya langsung ke toko.\n"
            "4. Pahami maksud kalimat pelanggan meskipun ada typo, kata singkatan, atau bahasa santai.\n\n"
            "=== DOKUMEN PENGETAHUAN TOKO ===\n"
            f"{KNOWLEDGE_CACHE}\n"
            "================================"
        )

        # Panggil API Nexotao
        response = client.chat.completions.create(
            model="gpt-4o-mini", # Atau ganti model nexotao lain pilihanmu
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.3 # Temperature rendah agar jawaban tetap fokus & faktual
        )

        bot_reply = response.choices[0].message.content if response.choices else "Maaf Kak, AI belum bisa merespons saat ini."
        return jsonify({'response': bot_reply})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'response': f'Terjadi kendala pada sistem CS AI: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
