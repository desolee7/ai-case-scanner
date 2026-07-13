class HackathonConfig:
    """Настройки парсера хакатонов"""
    
    # Категории Kaggle для сбора
    INCLUDE_CATEGORIES = [
        'Featured',      # премиальные соревнования с призами
        'Research',      # научные задачи
        'Hackathons',    # хакатоны
        'Simulations',   # симуляции (RL, агенты)
    ]


hackathon_config = HackathonConfig()