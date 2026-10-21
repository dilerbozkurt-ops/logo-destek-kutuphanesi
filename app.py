from flask import Flask, render_template_string, request, send_from_directory
import json
import os

app = Flask(__name__)

JSON_FILE = 'kutuphane_verileri.json'

def load_data():
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

qa_data = load_data()

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Logo Destek Kütüphanesi</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8f9fa; margin: 0; padding: 20px; }
        .container { max-width: 1100px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { color: #C8102E; font-size: 28px; margin-bottom: 20px; }
        .search-box { display: flex; gap: 10px; max-width: 700px; margin: 0 auto 30px auto; }
        input[type="text"] { flex: 1; padding: 14px 18px; font-size: 16px; border: 1px solid #ced4da; border-radius: 8px; outline: none; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
        input[type="text"]:focus { border-color: #C8102E; }
        button.search-btn { padding: 14px 28px; background-color: #C8102E; color: white; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; font-weight: 600; }
        button.search-btn:hover { background-color: #a00d25; }
        
        .result-card { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; margin-bottom: 25px; padding: 24px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
        .question-title { font-size: 17px; font-weight: 700; color: #1e293b; margin-bottom: 16px; line-height: 1.5; display: flex; align-items: flex-start; gap: 8px; }
        .question-title::before { content: "S:"; color: #8b5cf6; font-weight: 800; }
        
        .answer-content { color: #334155; font-size: 15px; line-height: 1.7; margin-bottom: 20px; padding: 12px; background: #f8fafc; border-radius: 8px; }
        .answer-content img { max-width: 100%; height: auto; border-radius: 8px; border: 1px solid #e2e8f0; margin: 15px 0; display: block; }
        
        .card-footer { display: flex; justify-content: space-between; align-items: center; border-top: 1px dashed #e2e8f0; padding-top: 15px; margin-top: 15px; flex-wrap: wrap; gap: 10px; }
        .tags { display: flex; gap: 8px; flex-wrap: wrap; }
        .tag { background-color: #f1f5f9; color: #64748b; padding: 6px 12px; border-radius: 6px; font-size: 12px; font-weight: 600; text-transform: uppercase; }
        .tag.purple { background-color: #f3e8ff; color: #7e22ce; }
        
        .copy-btn { background-color: #8b5cf6; color: white; border: none; padding: 8px 16px; border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer; transition: background 0.2s; }
        .copy-btn:hover { background-color: #7c3aed; }
        .count-info { color: #64748b; font-size: 14px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Logo Destek Asistanı</h1>
            <form method="POST" class="search-box">
                <input type="text" name="query" placeholder="Soru veya hata kodu arayın..." value="{{ query or '' }}" required>
                <button type="submit" class="search-btn">Ara</button>
            </form>
        </div>

        {% if results is not none %}
            <div class="count-info"><b>{{ results|length }}</b> sonuç bulundu.</div>
            {% for item in results %}
                <div class="result-card">
                    <div class="question-title">{{ item.question }}</div>
                    <div class="answer-content" id="ans-{{ loop.index }}">
                        {{ item.answer_html | safe }}
                    </div>
                    <div class="card-footer">
                        <div class="tags">
                            <span class="tag purple">Destek</span>
                            <span class="tag purple">Çözüm</span>
                        </div>
                        <button class="copy-btn" onclick="copyAnswer('ans-{{ loop.index }}')">Çözüm Adımlarını Kopyala</button>
                    </div>
                </div>
            {% endfor %}
        {% endif %}
    </div>

    <script>
    function copyAnswer(elementId) {
        var text = document.getElementById(elementId).innerText;
        navigator.clipboard.writeText(text).then(function() {
            alert('Çözüm adımları panoya kopyalandı!');
        });
    }
    </script>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    results = None
    query = ""
    if request.method == 'POST':
        query = request.form.get('query', '').strip().lower()
        if query:
            query_words = query.split()
            results = []
            for item in qa_data:
                q_text = item['question'].lower()
                a_text = item['answer_html'].lower()
                if all(word in q_text or word in a_text for word in query_words):
                    results.append(item)
    return render_template_string(HTML_TEMPLATE, results=results, query=query)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)