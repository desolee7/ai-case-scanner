"""Анализатор данных через LLM"""
import json
import re
import signal
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
  "detected_keywords": ["ключевое", "слово"],
  "dataset_suggestion": "Какой датасет нужен для реализации (1-2 предложения)"
}}

Если это не AI-кейс, верни:
{{
  "is_ai_case": false,
  "confidence": 0.0
}}"""


class AIAnalyzer:
    
    def __init__(self):
        self.llm = LLMClient()
        self.stop_requested = False
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        print("\n\nПрерывание... Сохраняю прогресс.")
        self.stop_requested = True
    
    def analyze_news(self, limit: int = None):
        self.stop_requested = False
        session = db.get_session()
        
        session.execute(text("UPDATE ai_insights SET status = 'old' WHERE status = 'new'"))
        session.commit()
        
        query = "SELECT id, source, title, content FROM news WHERE status = 'new'"
        if limit:
            query += f" LIMIT {limit}"
        rows = session.execute(text(query)).fetchall()
        print(f"Анализ новостей: {len(rows)}")
        session.close()
        
        for row in rows:
            if self.stop_requested:
                print("Анализ прерван пользователем.")
                break
            
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
        self.stop_requested = False
        session = db.get_session()
        
        session.execute(text("UPDATE ai_insights SET status = 'old' WHERE status = 'new'"))
        session.commit()
        
        query = "SELECT id, organizer, title, description FROM hackathons WHERE status = 'new'"
        if limit:
            query += f" LIMIT {limit}"
        rows = session.execute(text(query)).fetchall()
        print(f"Анализ хакатонов: {len(rows)}")
        session.close()
        
        for row in rows:
            if self.stop_requested:
                print("Анализ прерван пользователем.")
                break
            
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
        
        log = AnalyticsLog(
            source_type=source_type,
            source_id=source_id,
            model_used=analytics_config.MODEL,
            prompt=prompt[:500],
            raw_response=response[:2000],
        )
        session.add(log)
        
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
            if source_type == 'news':
                row = session.execute(
                    text("SELECT content, link FROM news WHERE id = :id"),
                    {"id": source_id}
                ).fetchone()
            else:
                row = session.execute(
                    text("SELECT description, source_url FROM hackathons WHERE id = :id"),
                    {"id": source_id}
                ).fetchone()
            
            source_text = row[0] if row else ''
            source_link = row[1] if row else ''
            
            insight = AIInsight(
                source_type=source_type,
                source_id=source_id,
                title=data.get('title', ''),
                description=source_text[:2000],
                potential_ai_solution=data.get('potential_ai_solution', ''),
                detected_keywords=json.dumps(data.get('detected_keywords', [])),
                confidence_score=data.get('confidence', 0),
                model_version=analytics_config.MODEL,
                source_url=source_link,
                dataset_suggestion=data.get('dataset_suggestion', ''),
                status='new',
            )
            session.add(insight)
            print(f"  AI-кейс: {data.get('title', '')[:80]}")
        
        table = 'news' if source_type == 'news' else 'hackathons'
        session.execute(
            text(f"UPDATE {table} SET status = 'analyzed' WHERE id = :id"),
            {"id": source_id}
        )
        
        session.commit()
        session.close()