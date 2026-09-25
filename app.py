import json
import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

NEXOTAO_API_KEY = os.getenv("NEXOTAO_API_KEY", "sk-nexo-IV3zf2wP-S_TKzpIrd2GqI2EpMx9aI1D")
NEXOTAO_URL = "https://api.nexotao.com/v1/chat/completions"

CONTEXT_FILE = "context.json"

def load_context():
    with open(CONTEXT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_context(data):
    with open(CONTEXT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@app.route("/")
def index():
    context_data = load_context()
    return render_template("index.html", store_name=context_data.get("store_name", "Customer Service"))

@app.route("/admin")
def admin():
    context_data = load_context()
    return render_template("admin.html", data=context_data)

@app.route("/api/save-context", methods=["POST"])
def api_save_context():
    data = request.json
    save_context(data)
    return jsonify({"status": "success", "message": "Konteks berhasil diperbarui!"})

@app.route("/api/chat", methods=["POST"])
def api_chat():
    user_message = request.json.get("message", "")
    if not user_message:
        return jsonify({"error": "Pesan tidak boleh kosong"}), 400

    context_data = load_context()
    
    full_system_prompt = f"{context_data.get('system_instruction')}\nDATA:\n{context_data.get('business_info')}"

    headers = {
        "Authorization": f"Bearer {NEXOTAO_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "nova-micro",
        "messages": [
            {"role": "system", "content": full_system_prompt},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.3,
        "max_tokens": 180  # MEMBATASI OUTPUT AGAR HEMAT TOKEN
    }

    try:
        response = requests.post(NEXOTAO_URL, headers=headers, json=payload, timeout=30)
        res_data = response.json()
        
        if response.status_code == 200 and "choices" in res_data:
            reply = res_data["choices"][0]["message"]["content"]
            return jsonify({"reply": reply})
        else:
            return jsonify({"error": res_data}), response.status_code
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
