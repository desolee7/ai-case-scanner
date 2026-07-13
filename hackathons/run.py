"""
Точка входа модуля хакатонов.
Первый запуск — все хакатоны (включая прошедшие).
Последующие — только новые.
"""
import json
from datetime import datetime
from pathlib import Path
from hackathons.kaggle_scraper import KaggleScraper
from hackathons.parser import HackathonParser


def load_existing_ids(data_dir: Path) -> set:
    """Загрузить ID уже сохранённых хакатонов"""
    existing = set()
    for f in data_dir.glob('hackathons_*.json'):
        with open(f, 'r', encoding='utf-8') as fh:
            for item in json.load(fh):
                if item.get('source_id'):
                    existing.add(item['source_id'])
    return existing


def main():
    print("=" * 60)
    print("МОДУЛЬ СБОРА ХАКАТОНОВ")
    print("Поиск AI-кейсов для госорганов")
    print("=" * 60)
    
    # Определяем режим запуска
    data_dir = Path(__file__).parent / 'data'
    data_dir.mkdir(exist_ok=True)
    
    existing_ids = load_existing_ids(data_dir)
    is_first_run = len(existing_ids) == 0
    
    if is_first_run:
        print("Первый запуск — собираем и прошедшие хакатоны")
        include_past = True
    else:
        print(f"Уже сохранено: {len(existing_ids)} хакатонов")
        print("Ищем только новые")
        include_past = False
    
    # Этап 1: Сбор данных
    scraper = KaggleScraper()
    raw_events = scraper.get_competitions(include_past=include_past)
    
    # Этап 2-3: Парсинг и нормализация
    parser = HackathonParser()
    ai_events = parser.parse_and_filter(raw_events)
    
    # Отфильтровываем уже сохранённые
    new_events = [e for e in ai_events if e['source_id'] not in existing_ids]
    
    if not new_events:
        print("\nНовых хакатонов нет")
        return
    
    # Этап 4: Сохранение
    filename = f"hackathons_{len(new_events)}items_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.json"
    filepath = data_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(new_events, f, ensure_ascii=False, indent=2)
    
    print(f"\nСохранено новых хакатонов: {len(new_events)} → {filepath}")
    
    # Вывод
    for event in new_events:
        print(f"\n{event['title']}")
        print(f"   Категория: {event['category']} | Дедлайн: {event['end_date'][:10] if event['end_date'] else 'нет'}")
        print(f"   Ключевые слова: {', '.join(event['matched_keywords'][:5])}")


if __name__ == '__main__':
    main()