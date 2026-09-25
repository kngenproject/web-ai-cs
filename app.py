from flask import Flask, render_template, request, jsonify
import os
import glob
from google import genai

app = Flask(__name__)

# Masukkan Gemini API Key kamu di sini atau set via Environment Variable Vercel
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "MASUKKAN_API_KEY_GEMINI_DI_SINI")

# Inisialisasi Client Gemini
client = None
if GEMINI_API_KEY and GEMINI_API_KEY != "MASUKKAN_API_KEY_GEMINI_DI_SINI":
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"Gagal inisialisasi Gemini: {e}")

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
        load_knowledge_base() # Membaca ulang isi .txt jika ada perubahan file
        data = request.get_json() or {}
        user_msg = data.get('message', '').strip()
        
        if not user_msg:
            return jsonify({'response': 'Mohon tuliskan pertanyaan Kakak ya 😊'})

        if not client:
            return jsonify({
                'response': 'Halo Kak! Sistem AI sedang dalam penyiapan (API Key belum terpasang di Vercel/app.py). Mohon hubungi admin toko ya.'
            })

        # SYSTEM PROMPT: Memaksa Gemini berpikir HANYA berpatokan pada dokumen toko
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

        # Meminta Gemini 2.5 Flash memproses jawaban
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_msg,
            config={'system_instruction': system_instruction}
        )

        bot_reply = response.text if response.text else "Maaf Kak, AI belum bisa merespons saat ini."
        return jsonify({'response': bot_reply})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'response': f'Terjadi kendala pada sistem CS AI: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
