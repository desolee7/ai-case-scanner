"""
Скачивание файлов контрактов по прямым ссылкам из Clearspending API.
"""
import time
from pathlib import Path
import requests
from shared.config import config


class ContractDownloader:
    """Скачивает PDF/DOCX файлы контрактов"""
    
    def __init__(self, download_dir: str = None):
        if download_dir is None:
            download_dir = Path(__file__).parent / 'data' / 'documents'
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        })
    
    def download_contract_files(self, regnum: str, files: list) -> list:
        """
        Скачать все файлы одного контракта.
        
        Параметры:
        - regnum: реестровый номер контракта
        - files: список словарей с 'url' и 'fileName'
        
        Возвращает: список локальных путей к файлам
        """
        contract_dir = self.download_dir / regnum
        contract_dir.mkdir(exist_ok=True)
        
        downloaded = []
        for file_info in files:
            url = file_info.get('url', '')
            filename = file_info.get('fileName', f'file_{len(downloaded)}')
            
            if not url:
                continue
            
            filepath = contract_dir / filename
            if filepath.exists():
                downloaded.append(str(filepath))
                continue
            
            try:
                response = self.session.get(url, timeout=config.REQUEST_TIMEOUT)
                response.raise_for_status()
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                downloaded.append(str(filepath))
                time.sleep(0.3)  # пауза между файлами
                
            except Exception as e:
                print(f"  ⚠ {filename}: {e}")
        
        return downloaded
    
    def download_from_contract(self, contract: dict) -> list:
        """
        Скачать файлы из метаданных контракта.
        Использует поля 'scan' и 'attachments' из Clearspending.
        """
        regnum = contract.get('regnum', 'unknown')
        
        # Собираем все файлы
        all_files = []
        
        # Сканы (PDF)
        for scan in contract.get('scan', []):
            all_files.append(scan)
        
        # Вложения
        for attachment in contract.get('attachments', {}).get('attachment', []):
            all_files.append(attachment)
        
        if not all_files:
            return []
        
        print(f"  {regnum}: {len(all_files)} файлов...")
        return self.download_contract_files(regnum, all_files)
    
    def close(self):
        self.session.close()