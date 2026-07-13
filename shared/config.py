class Config:
    REQUEST_DELAY = 0.5
    REQUEST_TIMEOUT = 30
    MAX_RETRIES = 3
    BATCH_SIZE = 100
    LOCAL_STORAGE_PATH = './data'
    
    # PostgreSQL
    DB_HOST = 'localhost'
    DB_PORT = 5432
    DB_NAME = 'goszakupki'
    DB_USER = 'postgres'
    DB_PASSWORD = '190224'


config = Config()