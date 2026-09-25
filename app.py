from flask import Flask, render_template, request, jsonify
import json
import requests
import os

app = Flask(__name__)

# Load context data
def load_context():
    try:
        with open('context.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        return {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json() or {}
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'response': 'Mohon tuliskan pertanyaan Kakak ya 😊'})

        context_data = load_context()

        # System prompt dengan instruksi ramah & pembatasan ketat
        system_instruction = (
            "Kamu adalah Customer Service AI resmi Toko Buah ABS Kepanjen yang sangat ramah, sopan, dan hangat. "
            "Selalu sapa pelanggan dengan santun (gunakan panggilan Kak/Bunda). "
            "Gunakan emotikon yang relevan. "
            "Tugasmu HANYA menjawab pertanyaan seputar Toko Buah ABS Kepanjen (stok buah, parcel, lokasi, jam buka, dan loker) "
            "berdasarkan data konteks berikut. Jika ditanya hal di luar topik, tolak dengan sopan.\n\n"
            f"Konteks Data: {json.dumps(context_data, ensure_ascii=False)}"
        )

        # Pemanggilan API Nova Micro / Nexotao (Sesuaikan URL & API Key jika ada)
        # Jika API luar bermasalah, diproteksi try-except agar web tidak error
        try:
            # Contoh struktur request API
            payload = {
                "model": "nova-micro",
                "messages": [
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_message}
                ],
                "max_tokens": 150
            }
            
            # Ganti URL ini jika menggunakan endpoint nexotao/custom API kamu
            api_url = "https://api.nexotao.com/v1/chat/completions" 
            
            response = requests.post(
                api_url, 
                json=payload, 
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                res_data = response.json()
                ai_reply = res_data['choices'][0]['message']['content']
                return jsonify({'response': ai_reply})
            else:
                # Fallback ramah jika API sibuk
                return jsonify({'response': 'Halo Kak! 😊 CS AI sedang menyesuaikan koneksi API. Untuk info cepat Toko Buah ABS Kepanjen, silakan tanyakan jam buka, lokasi, atau stok parcel ya!'})

        except Exception as api_err:
            # Fallback jika panggilan API timeout/gagal
            return jsonify({'response': 'Halo Kak! 😊 Maaf ada sedikit kendala jaringan ke server AI. Tapi Toko Buah ABS Kepanjen tetap buka setiap hari dari jam 08.00 - 21.00 WIB yaa 🍎🍊'})

    except Exception as e:
        return jsonify({'response': f'Terjadi kesalahan sistem: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
