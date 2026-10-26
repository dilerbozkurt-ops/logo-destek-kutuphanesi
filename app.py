import re
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
        print("Google Yanıtı:", response.text)
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
    <style>
        .dropdown { position: relative; display: inline-block; }
        .dropdown-content {
            display: none;
            position: absolute;
            right: 0;
            background-color: #ffffff;
            min-width: 220px;
            box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.15);
            border-radius: 8px;
            padding: 12px;
            z-index: 1000;
            border: 1px solid #e2e8f0;
        }
        .dropdown.active .dropdown-content { display: block; }
    </style>
</head>
<body class="bg-gray-100 min-h-screen py-8 px-4">
    <div class="max-w-5xl mx-auto">
        <h1 class="text-3xl font-bold text-center text-gray-800 mb-6">Logo Destek Kütüphanesi</h1>
        
        <!-- Arama ve Filtreleme Formu -->
        <form method="GET" action="/" id="searchForm" class="mb-8 bg-white p-4 rounded-xl shadow-sm border border-gray-200">
            <div class="grid grid-cols-1 md:grid-cols-12 gap-3 items-end">
                
                <!-- Ad Soyad -->
                <div class="md:col-span-3">
                    <label class="block text-xs font-semibold text-gray-500 mb-1">ADINIZ SOYADINIZ</label>
                    <input type="text" name="user_name" value="{{ user_name }}" required placeholder="Örn: Ahmet Yılmaz" 
                           class="w-full px-3 py-2.5 rounded-lg border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-purple-600">
                </div>

                <!-- Arama Kutusu -->
                <div class="md:col-span-5">
                    <label class="block text-xs font-semibold text-gray-500 mb-1">ARAMA</label>
                    <input type="text" name="q" value="{{ query }}" placeholder="Sorunuzu veya anahtar kelimeyi yazın..." 
                           class="w-full px-4 py-2.5 rounded-lg border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-purple-600">
                </div>

                <!-- Filtreler Dropdown Butonu -->
                <div class="md:col-span-2 relative">
                    <label class="block text-xs font-semibold text-gray-500 mb-1">KATEGORİ/PROJE</label>
                    <div class="dropdown w-full">
                        <button type="button" id="dropbtn" class="w-full bg-gray-50 text-gray-700 border border-gray-300 px-3 py-2.5 rounded-lg text-sm font-medium flex justify-between items-center hover:bg-gray-100">
                            <span>🔍 Filtreler</span>
                            <span class="text-xs">▼</span>
                        </button>
                        <div class="dropdown-content" id="dropdownMenu">
                            <h4 class="text-xs font-bold text-purple-700 uppercase mb-2">PROJE</h4>
                            {% for proj in ['Vestel', 'Samsung', 'Bsh', 'Genel'] %}
                            <label class="block text-xs text-gray-700 mb-1 cursor-pointer">
                                <input type="checkbox" name="proj" value="{{ proj }}" {% if proj in selected_projs %}checked{% endif %} class="mr-1.5"> {{ proj }}
                            </label>
                            {% endfor %}

                            <h4 class="text-xs font-bold text-purple-700 uppercase mt-3 mb-2">KATEGORİ</h4>
                            {% for tag in ['Payer', 'E2e', 'Ökc', 'B.Transfer', 'İnterpay', 'S.Online', 'Ceva/Sub', 'E-Devlet', 'Ahb'] %}
                            <label class="block text-xs text-gray-700 mb-1 cursor-pointer">
                                <input type="checkbox" name="tag" value="{{ tag }}" {% if tag in selected_tags %}checked{% endif %} class="mr-1.5"> {{ tag }}
                            </label>
                            {% endfor %}
                        </div>
                    </div>
                </div>

                <!-- Ara Butonu -->
                <div class="md:col-span-2">
                    <button type="submit" class="w-full bg-purple-600 text-white px-4 py-2.5 rounded-lg text-sm font-medium hover:bg-purple-700 transition">Ara</button>
                </div>

            </div>
        </form>

        {% if query or selected_projs or selected_tags %}
            <p class="text-gray-600 mb-4">Sonuçlar için <strong>{{ sonuçlar|length }}</strong> kayıt bulundu.</p>
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
                {% if query or selected_projs or selected_tags %}
                    <p class="text-center text-gray-500 mt-8">Aramanızla veya seçtiğiniz filtrelerle eşleşen bir kayıt bulunamadı.</p>
                {% endif %}
            {% endfor %}
        </div>
    </div>

    <script>
        const dropbtn = document.getElementById('dropbtn');
        const dropdown = document.querySelector('.dropdown');

        if (dropbtn) {
            dropbtn.addEventListener('click', function(e) {
                e.stopPropagation();
                dropdown.classList.toggle('active');
            });
        }

        document.addEventListener('click', function() {
            if (dropdown) dropdown.classList.remove('active');
        });

        if (dropdown) {
            dropdown.addEventListener('click', function(e) {
                e.stopPropagation();
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    query = request.args.get('q', '').strip()
    user_name_input = request.args.get('user_name', '').strip()
    selected_projs = request.args.getlist('proj')
    selected_tags = request.args.getlist('tag')
    
    saved_user_name = request.cookies.get('user_name', '')
    user_name = user_name_input or saved_user_name or "İsimsiz Kullanıcı"
    
    veriler = verileri_yukle()
    sonuçlar = []

    if query or selected_projs or selected_tags:
        log_detay = f"Sorgu: {query} | Projeler: {','.join(selected_projs)} | Etiketler: {','.join(selected_tags)}"
        log_gonder(user_name, "ARAMA", log_detay)

        for item in veriler:
            item_html = item.get('answer_html', '') + " " + item.get('question', '')
            item_text = item_html.lower()
            
            # Arama metni kontrolü
            matches_query = not query or query.lower() in item_text

            # Proje kontrolü (Doğrudan badge-project sınıfını regex ile arar)
            matches_proj = True
            if selected_projs:
                matches_proj = False
                for p in selected_projs:
                    pattern = rf'<span class=["\']badge-project["\']>\s*{p}\s*</span>'
                    if re.search(pattern, item_html, re.IGNORECASE):
                        matches_proj = True
                        break

            # Kategori/Etiket kontrolü
            item_tags = item.get('tags', '').lower()
            matches_tag = not selected_tags or any(t.lower() in item_text or t.lower() in item_tags for t in selected_tags)

            if matches_query and matches_proj and matches_tag:
                sonuçlar.append(item)
    else:
        if user_name_input:
            log_gonder(user_name, "GİRİŞ / İSİM KAYDI")

    resp = make_response(render_template_string(
        HTML_TEMPLATE, 
        sonuçlar=sonuçlar, 
        query=query, 
        user_name=user_name if user_name != "İsimsiz Kullanıcı" else "",
        selected_projs=selected_projs,
        selected_tags=selected_tags
    ))
    
    if user_name_input:
        resp.set_cookie('user_name', user_name_input, max_age=60*60*24*30)
    return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
