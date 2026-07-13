"""Анализатор данных через LLM"""
import json
import re
from analytics.llm_client import LLMClient
from analytics.config import analytics_config
from shared.database import db
from shared.models import AIInsight, AnalyticsLog
from sqlalchemy import text


PROMPT_TEMPLATE = """Проанализируй следующий текст и определи, можно ли из него извлечь потенциальный AI-кейс.

AI-кейс — это задача, которую можно решить с помощью искусственного интеллекта, машинного обучения, компьютерного зрения, NLP или других AI-технологий.

Учитывай как прямые упоминания AI, так и косвенные:
- Автоматизация процессов
- Анализ данных
- Классификация, прогнозирование
- Работа с текстами, изображениями, видео
- Оптимизация, поиск аномалий

Источник: {source}
Тип: {source_type}
Заголовок: {title}
Описание: {description}

Ответь СТРОГО в формате JSON без дополнительного текста:
{{
  "is_ai_case": true/false,
  "title": "Краткое название AI-кейса (5-10 слов)",
  "potential_ai_solution": "Какое AI-решение можно предложить (2-3 предложения)",
  "confidence": 0.0-1.0,
  "detected_keywords": ["ключевое", "слово"]
}}

Если это не AI-кейс, верни:
{{
  "is_ai_case": false,
  "confidence": 0.0
}}"""


class AIAnalyzer:
    
    def __init__(self):
        self.llm = LLMClient()
    
    def analyze_news(self, limit: int = None):
        session = db.get_session()
        
        # Помечаем старые инсайты
        session.execute(text("UPDATE ai_insights SET status = 'old' WHERE status = 'new'"))
        session.commit()
        
        query = "SELECT id, source, title, content FROM news WHERE status = 'new'"
        if limit:
            query += f" LIMIT {limit}"
        rows = session.execute(text(query)).fetchall()
        print(f"Анализ новостей: {len(rows)}")
        session.close()
        
        for row in rows:
            prompt = PROMPT_TEMPLATE.format(
                source=row[1],
                source_type='news',
                title=row[2],
                description=(row[3] or '')[:2000]
            )
            response = self.llm.analyze(prompt)
            if response:
                self._process_response(response, 'news', row[0], prompt)
    
    def analyze_hackathons(self, limit: int = None):
        session = db.get_session()
        
        # Помечаем старые инсайты
        session.execute(text("UPDATE ai_insights SET status = 'old' WHERE status = 'new'"))
        session.commit()
        
        query = "SELECT id, organizer, title, description FROM hackathons WHERE status = 'new'"
        if limit:
            query += f" LIMIT {limit}"
        rows = session.execute(text(query)).fetchall()
        print(f"Анализ хакатонов: {len(rows)}")
        session.close()
        
        for row in rows:
            prompt = PROMPT_TEMPLATE.format(
                source=row[1],
                source_type='hackathon',
                title=row[2],
                description=(row[3] or '')[:2000]
            )
            response = self.llm.analyze(prompt)
            if response:
                self._process_response(response, 'hackathon', row[0], prompt)
    
    def _process_response(self, response: str, source_type: str, source_id: int, prompt: str):
        session = db.get_session()
        
        # Сохраняем лог
        log = AnalyticsLog(
            source_type=source_type,
            source_id=source_id,
            model_used=analytics_config.MODEL,
            prompt=prompt[:500],
            raw_response=response[:2000],
        )
        session.add(log)
        
        # Парсим JSON
        try:
            data = json.loads(response)
        except json.JSONDecodeError:
            match = re.search(r'\{.*\}', response, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group())
                except:
                    data = None
            else:
                data = None
        
        if data and data.get('is_ai_case'):
            insight = AIInsight(
                source_type=source_type,
                source_id=source_id,
                title=data.get('title', ''),
                description=data.get('potential_ai_solution', ''),
                potential_ai_solution=data.get('potential_ai_solution', ''),
                detected_keywords=json.dumps(data.get('detected_keywords', [])),
                confidence_score=data.get('confidence', 0),
                model_version=analytics_config.MODEL,
                status='new',
            )
            session.add(insight)
            print(f"  AI-кейс: {data.get('title', '')[:80]}")
        
        # Обновляем статус источника
        table = 'news' if source_type == 'news' else 'hackathons'
        session.execute(
            text(f"UPDATE {table} SET status = 'analyzed' WHERE id = :id"),
            {"id": source_id}
        )
        
        session.commit()
        session.close()
        