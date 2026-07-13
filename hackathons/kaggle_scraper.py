"""
Сбор соревнований с Kaggle API.
"""
from kaggle.api.kaggle_api_extended import KaggleApi
from hackathons.config import hackathon_config


class KaggleScraper:
    
    def __init__(self):
        self.api = KaggleApi()
        self.api.authenticate()
    
    def get_competitions(self, include_past: bool = False):
        """
        Получить соревнования из прикладных категорий.
        
        Параметры:
        - include_past: True = все страницы, False = только активные
        """
        results = []
        page = 1
        
        while True:
            comps = self.api.competitions_list(
                sort_by='recentlyCreated',
                page=page
            )
            
            if not comps:
                break
            
            for comp in comps:
                if comp.category not in hackathon_config.INCLUDE_CATEGORIES:
                    continue
                
                if comp.ref.startswith('https://'):
                    url = comp.ref
                else:
                    url = f"https://www.kaggle.com/competitions/{comp.ref}"
                
                results.append({
                    'source': 'kaggle',
                    'source_url': url,
                    'source_id': url,
                    'title': comp.title,
                    'description': comp.description or '',
                    'start_date': str(comp.enabled_date) if comp.enabled_date else '',
                    'end_date': str(comp.deadline) if comp.deadline else '',
                    'deadline': str(comp.deadline) if comp.deadline else '',
                    'organizer': comp.organization_name or 'Kaggle',
                    'topics': ', '.join(t.name for t in (comp.tags or [])),
                    'category': comp.category,
                    'prize': str(comp.reward) if comp.reward else '',
                    'status': 'new',
                })
            
            if not include_past:
                break
            
            page += 1
        
        label = "все" if include_past else "активные"
        print(f"[Kaggle] Загружено: {len(results)} соревнований ({label})")
        return results