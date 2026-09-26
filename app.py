from flask import Flask, render_template, request, jsonify
import os
import glob
import re
from openai import OpenAI

app = Flask(__name__)

NEXOTAO_API_KEY = os.environ.get("NEXOTAO_API_KEY", "MASUKKAN_API_KEY_NEXOTAO_DI_SINI")

MODEL = "gemma-3-27b"

# Nomor WhatsApp Resmi Toko
WA_LOKER = "089516552310"
WA_TOKO = "081333527527"

client = None
if NEXOTAO_API_KEY and NEXOTAO_API_KEY != "MASUKKAN_API_KEY_NEXOTAO_DI_SINI":
    try:
        client = OpenAI(
            api_key=NEXOTAO_API_KEY,
            base_url="https://api.nexotao.com/v1"
        )
    except Exception as e:
        print(f"Gagal inisialisasi Nexotao: {e}")

# Quick Replies 0 Token
QUICK_REPLIES = {
    "halo": f"Halo Kak! 😊 Ada yang bisa kami bantu seputar stok buah, parcel, lokasi, atau loker di Toko Buah ABS Kepanjen?\n\n- WA Info Toko/Buah: {WA_TOKO}\n- WA Loker: {WA_LOKER}",
    "hai": f"Halo Kak! 😊 Ada yang bisa dibantu?\n- WA Toko/Order: {WA_TOKO}\n- WA Loker: {WA_LOKER}",
    "hi": f"Halo Kak! 😊 Ada yang bisa dibantu?\n- WA Toko/Order: {WA_TOKO}\n- WA Loker: {WA_LOKER}",
    "p": f"Halo Kak! Ada yang bisa dibantu seputar Toko Buah ABS Kepanjen? 😊\n- WA Toko: {WA_TOKO}\n- WA Loker: {WA_LOKER}",
    "ping": f"Halo Kak! Ada yang bisa dibantu? 😊\n- WA Toko: {WA_TOKO}\n- WA Loker: {WA_LOKER}",
    "selamat malam": "Selamat malam Kak! 😊 Ada yang bisa dibantu seputar Toko Buah ABS Kepanjen?",
    "selamat siang": "Selamat siang Kak! 😊 Ada yang bisa dibantu hari ini?",
    "selamat pagi": "Selamat pagi Kak! 😊 Ada yang bisa kami bantu?",
    "terima kasih": "Sama-sama Kak! Ditunggu kedatangannya di Toko Buah ABS Kepanjen ya 😊",
    "makasih": "Sama-sama Kak! Semoga sehat selalu 😊",
    "tes": "CS AI aktif dan siap membantu Kak! 😊"
}

def get_relevant_knowledge(user_msg):
    msg = user_msg.lower()
    target_files = []

    loker_keywords = ['loker', 'kerja', 'gaji', 'syarat', 'mess', 'berkas', 'lowongan', 'lamar', 'gawe', 'infoloker', 'ijazah', 'shift', 'jam kerja', 'cewek', 'wanita', 'perempuan', 'kerjaan']
    if any(k in msg for k in loker_keywords):
        target_files.extend(glob.glob("knowledge/*loker*.txt"))

    lokasi_keywords = ['alamat', 'lokasi', 'maps', 'buka', 'jam', 'instagram', 'ig', 'posisi', 'tempat', 'ancer', 'patokan', 'toko', 'daerah']
    if any(k in msg for k in lokasi_keywords):
        target_files.extend(glob.glob("knowledge/*lokasi*.txt"))
        target_files.extend(glob.glob("knowledge/*jam*.txt"))
        target_files.extend(glob.glob("knowledge/*sosmed*.txt"))

    produk_keywords = ['buah', 'parcel', 'stok', 'harga', 'parsel', 'paket', 'buah-buahan', 'ecer', 'grosir', 'apel', 'jeruk', 'anggur', 'mangga', 'beli', 'pesan']
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

        if not user_msg or len(user_msg.strip()) < 2:
            return jsonify({'response': 'Mohon tuliskan pertanyaan Kakak ya 😊'})

        user_msg = user_msg.strip()[:300]
        msg_lower = user_msg.lower()

        if msg_lower in QUICK_REPLIES:
            return jsonify({'response': QUICK_REPLIES[msg_lower]})

        if not client:
            return jsonify({'response': 'Sistem AI belum aktif (API Key belum terpasang).'})

        # ANALISIS INTENT LOKER (AI Mikir Dulu)
        loker_router_prompt = f"""Analisis maksud pertanyaan pelanggan berikut:

FULL_LOKER: Pelanggan meminta informasi lowongan kerja secara umum/keseluruhan/lengkap, atau bertanya apakah ada lowongan/loker.
PARTIAL_LOKER: Pelanggan hanya menanyakan SATU hal spesifik tentang loker (misal: hanya tanya gaji, jam kerja, mess/tempat tinggal, umur, atau cara kirim berkas).
OTHER: Bukan pertanyaan tentang lowongan kerja.

Pesan: "{user_msg}"

Jawab HANYA 1 kata pilihan: FULL_LOKER / PARTIAL_LOKER / OTHER"""

        loker_intent = "OTHER"

        try:
            router_response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "Kamu classifier intent. Output 1 kata saja."},
                    {"role": "user", "content": loker_router_prompt}
                ],
                temperature=0,
                max_tokens=10
            )

            loker_intent_raw = router_response.choices[0].message.content.strip().upper()
            loker_intent = re.sub(r'[`\n\s]+', '', loker_intent_raw).strip()

            if loker_intent not in {"FULL_LOKER", "PARTIAL_LOKER", "OTHER"}:
                loker_intent = "OTHER"

        except Exception as e:
            loker_intent = "OTHER"

        # BILA BUTUH INFO FULL LOKER
        if loker_intent == "FULL_LOKER":
            loker_path = "knowledge/loker.txt"
            try:
                with open(loker_path, "r", encoding="utf-8") as f:
                    loker_content = f.read().strip()
                if loker_content:
                    return jsonify({"response": f"Berikut info lowongan kerja Toko Buah ABS Kepanjen:\n\n{loker_content}\n\nUntuk pendaftaran/kirim berkas lamaran, hubungi WhatsApp Loker: {WA_LOKER}"})
            except Exception as e:
                pass

        # BILA HANYA TANYA SPESIFIK ATAU LAINNYA
        relevant_knowledge = get_relevant_knowledge(user_msg)

        system_instruction = (
            "Kamu CS Toko Buah ABS Kepanjen (panggil 'Kak').\n"
            "ATURAN MENJAWAB:\n"
            "1. Jawab SINGKAT, PADAT, dan LANGSUNG KE POIN UTAMA (maksimal 2-3 kalimat).\n"
            "2. Gunakan data toko di bawah.\n"
            f"3. Jika topik seputar LOKER/LAMARAN, sertakan kontak WA Loker: {WA_LOKER}.\n"
            f"4. Jika topik seputar PEMESANAN/BUAH/PARCEL/STOK, sertakan kontak WA Toko: {WA_TOKO}.\n"
            f"5. Jika informasi TIDAK ADA di data toko, minta maaf dan arahkan ke WA Toko ({WA_TOKO}) atau WA Loker ({WA_LOKER}) sesuai topik.\n\n"
            f"DATA TOKO:\n{relevant_knowledge}"
        )

        messages_to_ai = [{"role": "system", "content": system_instruction}]

        filtered_history = [h for h in chat_history[-2:] if h.get('role') in ['user', 'assistant'] and h.get('content')]
        while filtered_history and filtered_history[0]['role'] == 'assistant':
            filtered_history.pop(0)

        for hist in filtered_history:
            messages_to_ai.append({"role": hist['role'], "content": hist['content']})

        messages_to_ai.append({"role": "user", "content": user_msg})

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages_to_ai,
            temperature=0.2,
            max_tokens=90
        )

        bot_reply = response.choices[0].message.content if response.choices else f"Maaf Kak, untuk info lebih lanjut bisa kontak WhatsApp kami di {WA_TOKO} (Pemesanan) atau {WA_LOKER} (Loker)."
        return jsonify({'response': bot_reply})

    except Exception as e:
        return jsonify({'response': f'Terjadi kendala pada sistem CS AI: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
