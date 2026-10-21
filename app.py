from flask import Flask, render_template_string, request
import json
import os
import datetime

app = Flask(__name__)

# Verileri JSON dosyasından yükle
def verileri_yukle():
    if os.path.exists('kutuphane_verileri.json'):
        with open('kutuphane_verileri.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# Kullanım ve arama loglarını kaydetme fonksiyonu
def log_kaydet(islem_turu, detay=""):
    zaman = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ip_adresi = request.headers.get('X-Forwarded-For', request.remote_addr)
    log_satiri = f"[{zaman}] IP: {ip_adresi} | İşlem: {islem_turu} | Detay: {detay}\n"
    
    with open("kullanim_loglari.txt", "a", encoding="utf-8") as f:
        f.write(log_satiri)

# HTML Arayüz Şablonu
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Logo Destek Kütüphanesi</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 min-h-screen py-8 px-4">
    <div class="max-w-5xl mx-auto">
        <h1 class="text-3xl font-bold text-center text-gray-800 mb-6">Logo Destek Kütüphanesi</h1>
        
        <!-- Arama Formu -->
        <form method="GET" class="mb-8">
            <div class="flex gap-2">
                <input type="text" name="q" value="{{ query }}" placeholder="Sorunuzu veya anahtar kelimeyi yazın..." 
                       class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-600">
                <button type="submit" class="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 transition">Ara</button>
            </div>
        </form>

        {% if query %}
            <p class="text-gray-600 mb-4">"<strong>{{ query }}</strong>" için {{ sonuçlar|length }} sonuç bulundu.</p>
        {% endif %}

        <!-- Kart Yapısı -->
        <div class="space-y-4">
            {% for item in sonuçlar %}
            <div class="bg-white p-6 rounded-lg shadow-md border-l-4 border-purple-600">
                <h2 class="text-xl font-semibold text-gray-800 mb-2">{{ item.question }}</h2>
                <div class="text-gray-600 mb-4">{{ item.answer_html | safe }}</div>
                <button onclick="navigator.clipboard.writeText(`{{ item.question }}\n\n{{ item.answer_text }}`)" 
                        class="bg-purple-100 text-purple-700 px-4 py-2 rounded text-sm font-medium hover:bg-purple-200 transition">
                    📋 Çözüm Adımlarını Kopyala
                </button>
            </div>
            {% else %}
                {% if query %}
                    <p class="text-center text-gray-500 mt-8">Aramanızla eşleşen bir kayıt bulunamadı.</p>
                {% endif %}
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    query = request.args.get('q', '').strip()
    veriler = verileri_yukle()
    
    if query:
        # Arama yapıldığında log kaydet
        log_kaydet("ARAMA", query)
        sonuçlar = [item for item in veriler if query.lower() in item['question'].lower() or query.lower() in item.get('answer_text', '').lower()]
    else:
        # Siteye ilk giriş yapıldığında log kaydet
        log_kaydet("SİTE_GİRİŞİ")
        sonuçlar = []
        
    return render_template_string(HTML_TEMPLATE, sonuçlar=sonuçlar, query=query)

# Raporları / Logları görüntüleme ekranı (Gizli Rapor Sayfası)
@app.route('/rapor-log')
def rapor_goruntule():
    if os.path.exists("kullanim_loglari.txt"):
        with open("kullanim_loglari.txt", "r", encoding="utf-8") as f:
            loglar = f.readlines()
        return f"<pre style='font-family: monospace; padding: 20px;'>{''.join(loglar)}</pre>"
    return "Henüz kaydedilmiş bir kullanım kaydı bulunmuyor."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)