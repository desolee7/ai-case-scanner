"""
Скачивание файлов контрактов через curl.exe (поддерживает ГОСТ сертификаты).
"""
import subprocess
import time
from pathlib import Path
from shared.config import config


class ContractDownloader:
    """Скачивает PDF/DOCX файлы контрактов"""
    
    def __init__(self, download_dir: str = None):
        if download_dir is None:
            download_dir = Path(__file__).parent / 'data' / 'documents'
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
    
    def download_contract_files(self, regnum: str, files: list) -> list:
        if not regnum or regnum == 'unknown':
            return []
        
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
            
            if self._download_file(url, filepath):
                downloaded.append(str(filepath))
                time.sleep(0.3)
            else:
                print(f"  {filename}: ошибка скачивания")
        
        return downloaded
    
    def download_from_contract(self, contract: dict) -> list:
        regnum = contract.get('regnum') or contract.get('regNum', '')
        
        all_files = []
        
        for scan in contract.get('scan', []):
            all_files.append(scan)
        
        for attachment in contract.get('attachments', {}).get('attachment', []):
            all_files.append(attachment)
        
        if not all_files:
            return []
        
        if not regnum:
            print(f"  (без номера): {len(all_files)} файлов - пропущено")
            return []
        
        print(f"  {regnum}: {len(all_files)} файлов...")
        return self.download_contract_files(regnum, all_files)
    
    def _download_file(self, url: str, filepath: Path) -> bool:
        try:
            result = subprocess.run(
                ['curl.exe', '-s', '-L', '-k', '--max-time', '120', '-o', str(filepath), url],
                capture_output=True,
                encoding='utf-8',
                errors='replace'
            )
            return result.returncode == 0 and filepath.exists() and filepath.stat().st_size > 0
        except Exception as e:
            return False
    
    def close(self):
        pass