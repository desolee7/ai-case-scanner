import requests
from analytics.config import analytics_config


class LLMClient:
    
    def __init__(self):
        self.url = 'http://localhost:11434/api/chat'
        self.model = analytics_config.MODEL
    
    def analyze(self, prompt: str) -> str:
        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "Ты аналитик, который находит потенциальные AI-кейсы в текстах. Отвечай строго в формате JSON."},
                {"role": "user", "content": prompt}
            ],
            "stream": False,
            "options": {
                "temperature": analytics_config.TEMPERATURE,
                "num_predict": analytics_config.MAX_TOKENS,
            }
        }
        
        try:
            response = requests.post(self.url, json=body)
            data = response.json()
            return data.get('message', {}).get('content', '')
        except Exception as e:
            print(f"Ollama error: {e}")
            return None