from bs4 import BeautifulSoup
import json

def parse_html_to_json(html_file_path):
    with open(html_file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    qa_list = []
    
    # Soru başlıklarını barındıran veya S: içeren elemanları taptaze HTML içeriğiyle yakalıyoruz
    # Orijinal kütüphane yapısındaki paragrafları ve görselleri HTML olarak topluyoruz
    raw_content = str(soup)
    
    # 'S:' başlıklarına göre HTML bloklarını bölüyoruz
    import re
    blocks = re.split(r'(?=<p[^>]*>\s*S:|S:)', raw_content)

    for block in blocks:
        if 'S:' not in block:
            continue
        
        block_soup = BeautifulSoup(block, 'html.parser')
        
        # Soru başlığını alalım (S: ile başlayan kısım)
        text_content = block_soup.get_text()
        if 'S:' in text_content:
            q_match = re.search(r'S:(.*?)(?=C:|<img|$|\n)', text_content, re.DOTALL)
            question = q_match.group(1).strip() if q_match else "Soru Başlığı"
        else:
            question = "Destek Konusu"

        # Görseller dahil tüm cevap HTML'ini koruyoruz
        # C: sonrasındaki veya bloğun içindeki tüm HTML (img, table vb.)
        answer_html = str(block_soup)

        if question and len(question) > 3:
            qa_list.append({
                "question": question,
                "answer_html": answer_html
            })

    with open('kutuphane_verileri.json', 'w', encoding='utf-8') as json_file:
        json.dump(qa_list, json_file, ensure_ascii=False, indent=4)

    print(f"Başarılı! Toplam {len(qa_list)} soru-cevap görselleriyle birlikte aktarıldı.")

parse_html_to_json('Kütüphane.htm')