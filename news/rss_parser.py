"""
Парсер RSS-лент: Хабр, ТАСС, Интерфакс.
С загрузкой полного текста статей.
"""
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from news.config import news_config
from shared.config import config


class RSSParser:
    
    def __init__(self, full_content: bool = True):
        self.urls = news_config.RSS_URLS
        self.full_content = full_content
    
    def fetch_all(self) -> list:
        """Загрузить все RSS-ленты"""
        all_items = []
        
        for url in self.urls:
            source = self._get_source_name(url)
            print(f"Загрузка RSS: {source}")
            
            xml_content = self._fetch(url)
            if xml_content:
                items = self._parse(xml_content, source)
                
                if self.full_content:
                    print(f"  Загрузка полных текстов ({len(items)} статей)...")
                    for i, item in enumerate(items, 1):
                        if i % 10 == 0:
                            print(f"    {i}/{len(items)}")
                        full = self._fetch_full_content(item['link'], source)
                        if full:
                            item['content'] = full
                
                all_items.extend(items)
        
        print(f"[RSS] Всего загружено новостей: {len(all_items)}")
        return all_items
    
    def _fetch(self, url: str) -> str:
        """Загрузить RSS-ленту"""
        try:
            response = requests.get(url, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"  Ошибка загрузки RSS: {e}")
            return None
    
    def _parse(self, xml_content: str, source: str) -> list:
        """Разобрать RSS"""
        root = ET.fromstring(xml_content)
        items = []
        
        for item in root.findall('.//item'):
            link = item.findtext('link', '') or item.findtext('guid', '')
            
            items.append({
                'source': source,
                'external_id': link,
                'title': item.findtext('title', ''),
                'link': link,
                'date': item.findtext('pubDate', ''),
                'content': item.findtext('description', ''),
                'status': 'new',
            })
        
        print(f"  {source}: {len(items)} новостей")
        return items
    
    def _fetch_full_content(self, url: str, source: str) -> str:
        """Загрузить полный текст статьи"""
        try:
            response = requests.get(url, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            if 'habr' in source:
                article = soup.find('div', class_='article-body')
                if article:
                    return article.text.strip()[:3000]
            
            if 'tass' in source:
                article = soup.find('div', class_='article__text')
                if article:
                    return article.text.strip()[:3000]
            
            if 'interfax' in source:
                article = soup.find('article')
                if article:
                    return article.text.strip()[:3000]
            
            # Универсальный поиск
            for tag in soup.find_all(['article', 'main']):
                text = tag.text.strip()
                if len(text) > 500:
                    return text[:3000]
            
            return ''
            
        except Exception as e:
            return ''
    
    def _get_source_name(self, url: str) -> str:
        if 'habr' in url:
            return 'habr.com'
        elif 'tass' in url:
            return 'tass.ru'
        elif 'interfax' in url:
            return 'interfax.ru'
        return url