"""
Работа с базой данных PostgreSQL.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from shared.models import Base


class DatabaseManager:
    
    def __init__(self, host='localhost', port=5432, dbname='goszakupki', 
                 user='postgres', password='190224'):
        self.url = f"postgresql://{user}:{password}@{host}:{port}/{dbname}?client_encoding=utf8"
        self.engine = create_engine(self.url)
        self.Session = scoped_session(sessionmaker(bind=self.engine))
    
    def init_db(self):
        """Создать все таблицы"""
        Base.metadata.create_all(self.engine)
        print("База данных инициализирована")
    
    def get_session(self):
        """Получить сессию"""
        return self.Session()
    
    def save_all(self, items: list, model):
        """Сохранить список объектов в БД, пропуская дубликаты"""
        session = self.get_session()
        try:
            added = 0
            for item in items:
                # Ищем уникальный ключ
                if hasattr(model, 'external_id') and 'external_id' in item:
                    exists = session.query(model).filter_by(external_id=item['external_id']).first()
                elif hasattr(model, 'regnum') and 'regnum' in item:
                    exists = session.query(model).filter_by(regnum=item['regnum']).first()
                elif hasattr(model, 'source_url') and 'source_url' in item:
                    exists = session.query(model).filter_by(source_url=item['source_url']).first()
                else:
                    exists = False
                
                if not exists:
                    obj = model(**item)
                    session.add(obj)
                    added += 1
            
            session.commit()
            print(f"[DB] Сохранено: {added} новых записей в {model.__tablename__}")
        except Exception as e:
            session.rollback()
            print(f"[DB] Ошибка: {e}")
        finally:
            session.close()


# Экземпляр по умолчанию
db = DatabaseManager()