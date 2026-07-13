"""
Импорт данных из JSON-файлов в PostgreSQL.
"""
import json
from pathlib import Path
from datetime import datetime
from shared.database import db
from shared.models import Contract, News, Hackathon


def parse_date(date_str):
    if not date_str:
        return None
    formats = [
        '%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f',
        '%d.%m.%Y', '%a, %d %b %Y %H:%M:%S %Z', '%a, %d %b %Y %H:%M:%S %z',
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except:
            pass
    try:
        return datetime.fromisoformat(date_str.strip())
    except:
        pass
    return None


def import_contracts():
    data_dir = Path('goszakupki/data/documents')
    if not data_dir.exists():
        print("Нет данных контрактов")
        return
    
    for json_file in data_dir.glob('contracts_*.json'):
        print(f"Импорт: {json_file.name}")
        with open(json_file, 'r', encoding='utf-8') as f:
            contracts = json.load(f)
        
        clean = []
        for c in contracts:
            products = c.get('products', [])
            okpd2 = products[0].get('okpd2_code', '') if products else ''
            description = products[0].get('name', '') if products else ''
            
            clean.append({
                'regnum': c.get('regnum', ''),
                'customer_inn': c.get('customer_inn', ''),
                'supplier_inn': c.get('supplier_inn', ''),
                'price': c.get('price', 0),
                'sign_date': parse_date(c.get('sign_date')),
                'okpd2': okpd2,
                'description': description,
                'ei_link': c.get('url', ''),
                'status': 'new',
            })
        
        db.save_all(clean, Contract)


def import_news():
    data_dir = Path('news/data')
    if not data_dir.exists():
        print("Нет данных новостей")
        return
    
    for json_file in data_dir.glob('news_*.json'):
        print(f"Импорт: {json_file.name}")
        with open(json_file, 'r', encoding='utf-8') as f:
            news = json.load(f)
        
        clean = []
        for n in news:
            clean.append({
                'external_id': n.get('external_id', n.get('link', '')),
                'source': n.get('source', ''),
                'title': n.get('title', ''),
                'date': parse_date(n.get('date')),
                'link': n.get('link', ''),
                'content': n.get('content', ''),
                'status': 'new',
            })
        
        db.save_all(clean, News)


def import_hackathons():
    data_dir = Path('hackathons/data')
    if not data_dir.exists():
        print("Нет данных хакатонов")
        return
    
    for json_file in data_dir.glob('hackathons_*.json'):
        print(f"Импорт: {json_file.name}")
        with open(json_file, 'r', encoding='utf-8') as f:
            hackathons = json.load(f)
        
        clean = []
        for h in hackathons:
            clean.append({
                'source_url': h.get('source_id', h.get('url', '')),
                'title': h.get('title', ''),
                'start_date': parse_date(h.get('date')),
                'end_date': parse_date(h.get('end_date')),
                'organizer': h.get('organizer', ''),
                'topics': h.get('topics', ''),
                'description': h.get('description', ''),
                'status': 'new',
            })
        
        db.save_all(clean, Hackathon)


if __name__ == '__main__':
    print("=" * 50)
    print("ИМПОРТ ДАННЫХ В БД")
    print("=" * 50)
    
    import_contracts()
    import_hackathons()
    import_news()
    
    print("\nГотово!")