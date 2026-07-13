"""
Парсинг и нормализация данных о хакатонах.
Этапы 2-3 архитектуры: «Парсинг карточек» → «Извлечение и нормализация»
"""
from hackathons.filters import POSITIVE_PATTERNS, NEGATIVE_PATTERNS


class HackathonParser:
    
    def __init__(self):
        self.positive = [p.lower() for p in POSITIVE_PATTERNS]
        self.negative = [n.lower() for n in NEGATIVE_PATTERNS]
    
    def parse_and_filter(self, raw_events: list) -> list:
        """
        Фильтрует хакатоны по ключевым словам.
        Оставляет только те, где есть позитивные паттерны и нет негативных.
        
        Возвращает: список нормализованных словарей
        """
        filtered = []
        
        for event in raw_events:
            text = (
                event.get('title', '') + ' ' +
                event.get('description', '') + ' ' +
                event.get('topics', '')
            ).lower()
            
            # Проверяем негативные паттерны — если есть, пропускаем
            has_negative = any(pattern in text for pattern in self.negative)
            if has_negative:
                continue
            
            # Проверяем позитивные паттерны — должен быть хотя бы один
            has_positive = any(pattern in text for pattern in self.positive)
            if not has_positive:
                continue
            
            # Находим сработавшие ключевые слова
            matched_keywords = [p for p in self.positive if p in text]
            
            # Нормализуем и сохраняем
            normalized = self._normalize(event, matched_keywords)
            filtered.append(normalized)
        
        print(f"[Парсер] Отобрано AI-кейсов: {len(filtered)} из {len(raw_events)}")
        return filtered
    
    def _normalize(self, event: dict, matched_keywords: list) -> dict:
        """Приведение к единому формату (как в models.Hackathon)"""
        return {
            'source_type': 'hackathon',
            'source': event.get('source', ''),
            'source_id': event.get('source_url', ''),
            'title': event.get('title', ''),
            'description': event.get('description', ''),
            'url': event.get('source_url', ''),
            'date': event.get('start_date', ''),
            'end_date': event.get('end_date', ''),
            'organizer': event.get('organizer', ''),
            'topics': event.get('topics', ''),
            'prize': event.get('prize', ''),
            'category': event.get('category', ''),
            'matched_keywords': matched_keywords,  # для аналитического модуля
            'metadata': {
                'deadline': event.get('deadline', ''),
                'source': 'kaggle',
            },
            'status': 'new',
        }