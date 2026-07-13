"""
Точка входа модуля новостей.
Сохраняет все новости без фильтрации.
"""
import json
from datetime import datetime
from pathlib import Path
from news.rss_parser import RSSParser


def load_existing_ids(data_dir: Path) -> set:
    existing = set()
    for f in data_dir.glob('news_*.json'):
        with open(f, 'r', encoding='utf-8') as fh:
            for item in json.load(fh):
                if item.get('external_id'):
                    existing.add(item['external_id'])
    return existing


def main():
    print("=" * 60)
    print("МОДУЛЬ СБОРА НОВОСТЕЙ")
    print("=" * 60)
    
    data_dir = Path(__file__).parent / 'data'
    data_dir.mkdir(exist_ok=True)
    
    existing_ids = load_existing_ids(data_dir)
    print(f"Уже сохранено: {len(existing_ids)} новостей")
    
    rss = RSSParser()
    all_news = rss.fetch_all()
    
    if not all_news:
        print("Новости не загружены")
        return
    
    new_news = [n for n in all_news if n['external_id'] not in existing_ids]
    
    if not new_news:
        print("Новых новостей нет")
        return
    
    filename = f"news_{len(new_news)}items_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.json"
    filepath = data_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(new_news, f, ensure_ascii=False, indent=2)
    
    print(f"\nСохранено новых новостей: {len(new_news)} -> {filepath}")
    
    for news in new_news[:5]:
        print(f"  [{news['source']}] {news['title'][:80]}")


if __name__ == '__main__':
    main()