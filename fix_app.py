# fix_app.py - Jalankan di root folder proyek
import re
import os
from datetime import datetime

def backup_file(filename):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = f"{filename}.bak-{timestamp}"
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    with open(backup, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Backup: {backup}")
    return content

def fix_app_py():
    print("\n🔧 [1/2] Memperbaiki app.py...\n")
    
    original = backup_file('app.py')
    
    # FIX 1: Intent parsing ketat (regex)
    old_parse = '''loker_intent = (
                router_response.choices[0].message.content.strip().upper()
            )

            # Bersihkan kemungkinan formatting AI
            loker_intent = loker_intent.replace("`", "").strip()'''
    
    new_parse = '''loker_intent_raw = router_response.choices[0].message.content.strip().upper()
            # Ketat: remove backticks, newlines, extra spaces
            loker_intent = re.sub(r'[`\\n\\s]+', '', loker_intent_raw).strip()'''
    
    fix1 = original.replace(old_parse, new_parse)
    
    # FIX 2: Add re import
    fix2 = fix1.replace(
        'from flask import Flask, render_template, request, jsonify\nimport os\nimport glob\nfrom openai import OpenAI',
        'from flask import Flask, render_template, request, jsonify\nimport os\nimport glob\nimport re\nfrom openai import OpenAI'
    )
    
    # FIX 3: Input validation
    old_input = 'if not user_msg:\n            return jsonify({\'response\': \'Mohon tuliskan pertanyaan Kakak ya 😊\'})'
    new_input = '''if not user_msg or len(user_msg.strip()) < 2:
            return jsonify({'response': 'Mohon tuliskan pertanyaan Kakak ya 😊'})
        
        user_msg = user_msg.strip()[:500]  # Cap 500 chars'''
    
    fix3 = fix2.replace(old_input, new_input)
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(fix3)
    
    print("✅ app.py diperbaiki:")
    print("   • Intent parsing ketat (regex)")
    print("   • Input validation (max 500 chars)")
    print("   • Import re module")

def fix_readme():
    print("\n🔧 [2/2] Update README.md...\n")
    
    original = backup_file('README.md')
    
    # Update model reference
    fix1 = original.replace(
        'Model Ultra Efisien (`nova-micro`): Menggunakan model `nova-micro` via Nexotao API untuk eksekusi reasoning cepat dan biaya terjangkau.',
        'Model Ultra Efisien (`deepseek-v3-2`): Menggunakan model `deepseek-v3-2` via Nexotao API untuk reasoning mendalam dan respons berkualitas tinggi.'
    )
    
    fix2 = fix1.replace(
        '1. **Model Ultra Efisien (`nova-micro`)**',
        '1. **Model DeepSeek V3 (`deepseek-v3-2`)**'
    )
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(fix2)
    
    print("✅ README.md updated:")
    print("   • Model: nova-micro → deepseek-v3-2")

def main():
    print("""
╔════════════════════════════════════════╗
║   PERBAIKAN: CS AI ABS Kepanjen        ║
║   Auto-fix Script v1                   ║
╚════════════════════════════════════════╝
    """)
    
    if not os.path.exists('app.py'):
        print("❌ Error: app.py tidak ditemukan!")
        print("   Pastikan sudah 'cd' ke folder proyek")
        return False
    
    try:
        fix_app_py()
        fix_readme()
        
        print("\n" + "="*50)
        print("✅ SEMUA PERBAIKAN SELESAI!")
        print("="*50)
        print("""
Langkah selanjutnya:
  git add app.py README.md
  git commit -m "Fix: improve intent parsing, validation, docs"
  git push
        """)
        return True
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
