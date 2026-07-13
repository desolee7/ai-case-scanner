"""
Клиент для работы с Clearspending API v3 через curl.exe.

Что делает:
- Отправляет запросы с фильтрами (по одному ключевому слову за раз)
- Получает JSON-ответ со списком контрактов
- Объединяет результаты, убирает дубликаты по regnum
"""
import subprocess
import json
import time
from urllib.parse import urlencode
from shared.config import config


class ClearspendingClient:
    
    def __init__(self):
        self.base_url = 'http://openapi.clearspending.ru/restapi/v3/contracts/search/'
    
    def search_single(self, keyword: str, date_from: str = None, date_to: str = None, 
                      page: int = 1, per_page: int = 50):
        """
        Поиск по ОДНОМУ ключевому слову — одна страница.
        
        Параметры:
        - keyword: одно ключевое слово или фраза
        - date_from: начальная дата (YYYY-MM-DD)
        - date_to: конечная дата (YYYY-MM-DD)
        - page: номер страницы
        - per_page: результатов на странице (макс 50)
        
        Возвращает: JSON с результатами или None при ошибке
        """
        params = {
            'page': page,
            'perpage': per_page,
            'productsearch': keyword,
            'sort': '-signDate',
        }
        
        if date_from and date_to:
            d1 = date_from.split('-')
            d2 = date_to.split('-')
            params['daterange'] = f"{d1[2]}.{d1[1]}.{d1[0]}-{d2[2]}.{d2[1]}.{d2[0]}"
        
        url = self.base_url + '?' + urlencode(params)
        return self._curl_request(url)
    
    def search_all_pages(self, keyword: str, date_from: str = None, date_to: str = None):
        """
        Поиск по ОДНОМУ ключевому слову — все страницы.
        
        Возвращает: список всех найденных контрактов для данного слова
        """
        all_contracts = []
        page = 1
        
        while True:
            response = self.search_single(keyword, date_from, date_to, page=page)
            
            if not response:
                break
            
            data = response.get('contracts', {})
            contracts = data.get('data', [])
            
            if not contracts:
                break
            
            all_contracts.extend(contracts)
            
            total = data.get('total', 0)
            if len(all_contracts) >= total or len(all_contracts) >= 500:
                break
            
            page += 1
            time.sleep(config.REQUEST_DELAY)
        
        return all_contracts
    
    def search_all_queries(self, keywords: list, date_from: str = None, date_to: str = None):
        """
        Поиск по СПИСКУ ключевых слов — каждое слово отдельным запросом.
        Объединяет результаты, убирает дубликаты по regnum.
        
        Параметры:
        - keywords: список ключевых слов/фраз
        - date_from: начальная дата
        - date_to: конечная дата
        
        Возвращает: список уникальных контрактов
        """
        all_contracts = {}  # словарь для удаления дубликатов
        total_queries = len(keywords)
        
        print("=" * 60)
        print("ПОИСК КОНТРАКТОВ В CLEARSPENDING API")
        print(f"Запросов: {total_queries}")
        print(f"Период: {date_from or 'не указан'} — {date_to or 'не указан'}")
        print("=" * 60)
        
        for i, keyword in enumerate(keywords, 1):
            print(f"\n[{i}/{total_queries}] «{keyword}»", end=' ')
            
            contracts = self.search_all_pages(keyword, date_from, date_to)
            
            new_count = 0
            for contract in contracts:
                regnum = contract.get('regNum', '')
                if regnum and regnum not in all_contracts:
                    all_contracts[regnum] = contract
                    contract['_matched_query'] = keyword
                    new_count += 1
            
            print(f"— найдено {len(contracts)}, новых {new_count}")
            
            if i < total_queries:
                time.sleep(config.REQUEST_DELAY)
        
        unique = list(all_contracts.values())
        
        print("\n" + "=" * 60)
        print(f"ВСЕГО УНИКАЛЬНЫХ КОНТРАКТОВ: {len(unique)}")
        
        if unique:
            print("\nПервые 10 реестровых номеров:")
            for c in unique[:10]:
                regnum = c.get('regNum', '—')
                price = c.get('price', 0)
                date = c.get('signDate', '')[:10]
                print(f"  {regnum} | {price:,.0f} ₽ | {date}")
        
        return unique
    
    def _curl_request(self, url: str):
        """Выполнение запроса через curl.exe"""
        for attempt in range(1, config.MAX_RETRIES + 1):
            try:
                result = subprocess.run(
                    ['curl.exe', '-s', '-L', '--max-time', str(config.REQUEST_TIMEOUT), url],
                    capture_output=True,
                    encoding='utf-8',
                    errors='replace'
                )
                
                if result.returncode == 0 and result.stdout:
                    try:
                        return json.loads(result.stdout)
                    except json.JSONDecodeError:
                        if 'Data not found' in result.stdout:
                            return None  # API вернул "данных нет" — это не ошибка
                        print(f"\n  Ответ не JSON: {result.stdout[:100]}")
                        return None
                else:
                    if result.returncode != 0:
                        print(f"\n  curl code {result.returncode}")
                    
            except Exception as e:
                print(f"\n  Ошибка: {e}")
            
            if attempt < config.MAX_RETRIES:
                time.sleep(2 ** attempt)
        
        return None
    
    def close(self):
        pass