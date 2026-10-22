from flask import Flask, render_template_string, request, make_response
import json
import os
import datetime
import requests

app = Flask(__name__)

# Google Apps Script Web App URL Adresiniz
GOOGLE_SHEETS_URL = "https://script.google.com/macros/s/AKfycbzv-lH2KDKTtjynnXPrs1B4SHkWKCG-Wjnuyl65n68vM2r-n141vjHJop0ElyVuyvCT/exec"

# Verileri JSON dosyasından yükle
def verileri_yukle():
    if os.path.exists('kutuphane_verileri.json'):
        with open('kutuphane_verileri.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# Logları doğrudan Google E-Tablo'ya gönderen fonksiyon
def log_gonder(kullanici_adi, islem_turu, detay=""):
    zaman = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    payload = {
        "tarih": zaman,
        "kullanici": kullanici_adi,
        "islem": islem_turu,
        "detay": detay
    }
    try:
        response = requests.post(GOOGLE_SHEETS_URL, json=payload, timeout=10)
        print("Google Yanıtı:", response.text) # Render loglarında göreceğiz
    except Exception as e:
        print("Log gönderme hatası:", e)

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
        <form method="GET" class="mb-8 bg-white p-4 rounded-xl shadow-sm border border-gray-200">
            <div class="grid grid-cols-1 md:grid-cols-4 gap-3">
                <div class="md:col-span-1">
                    <label class="block text-xs font-semibold text-gray-500 mb-1">ADINIZ SOYADINIZ</label>
                    <input type="text" name="user_name" value="{{ user_name }}" required placeholder="Örn: Ahmet Yılmaz" 
                           class="w-full px-3 py-2.5 rounded-lg border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-purple-600">
                </div>
                <div class="md:col-span-3">
                    <label class="block text-xs font-semibold text-gray-500 mb-1">ARAMA</label>
                    <div class="flex gap-2">
                        <input type="text" name="q" value="{{ query }}" placeholder="Sorunuzu veya anahtar kelimeyi yazın..." 
                               class="w-full px-4 py-2.5 rounded-lg border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-purple-600">
                        <button type="submit" class="bg-purple-600 text-white px-6 py-2.5 rounded-lg text-sm font-medium hover:bg-purple-700 transition">Ara</button>
                    </div>
                </div>
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
    user_name_input = request.args.get('user_name', '').strip()
    saved_user_name = request.cookies.get('user_name', '')

    user_name = user_name_input or saved_user_name or "İsimsiz Kullanıcı"
    
    veriler = verileri_yukle()
    
    if query:
        # Arama logunu doğrudan Google Sheets'e gönder
        log_gonder(user_name, "ARAMA", query)
        sonuçlar = [item for item in veriler if query.lower() in item['question'].lower() or query.lower() in item.get('answer_text', '').lower()]
    else:
        if user_name_input:
            log_gonder(user_name, "GİRİŞ / İSİM KAYDI")
        sonuçlar = []

    resp = make_response(render_template_string(HTML_TEMPLATE, sonuçlar=sonuçlar, query=query, user_name=user_name if user_name != "İsimsiz Kullanıcı" else ""))
    if user_name_input:
        resp.set_cookie('user_name', user_name_input, max_age=60*60*24*30)  # 30 gün saklar
    return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
