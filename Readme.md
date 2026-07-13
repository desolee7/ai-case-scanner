# Ai cases

Система автоматического сбора и анализа данных для выявления AI-кейсов в госзакупках, хакатонах и новостях.

## Структура проекта

```
Autoparsing/
├── shared/
│   ├── config.py          # Общие настройки
│   ├── models.py          # Модели БД (SQLAlchemy)
│   ├── database.py        # Работа с PostgreSQL
│   ├── import_data.py     # Импорт JSON в БД
│   └── view_db.py         # Просмотр содержимого БД
├── goszakupki/
│   ├── api_client.py      # Клиент Clearspending API
│   ├── download_documents.py  # Скачивание файлов
│   ├── filters.py         # Ключевые слова и фильтры
│   ├── config.py          # Настройки модуля
│   ├── run.py             # Точка входа
│   └── data/              # Сохранённые JSON и документы
├── hackathons/
│   ├── kaggle_scraper.py  # Сбор с Kaggle API
│   ├── parser.py          # Фильтрация и нормализация
│   ├── filters.py         # Ключевые слова
│   ├── config.py          # Настройки модуля
│   ├── run.py             # Точка входа
│   └── data/              # Сохранённые JSON
├── news/
│   ├── rss_parser.py      # Парсер RSS-лент
│   ├── config.py          # Настройки модуля
│   ├── run.py             # Точка входа
│   └── data/              # Сохранённые JSON
├── run_all.py             # Планировщик всех модулей
├── requirements.txt       # Зависимости
└── README.md              # Этот файл

```

## Установка

### 1. Клонировать репозиторий

### 2. Создать виртуальное окружение

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

### 4. Установить PostgreSQL и создать базу

```bash
psql -U postgres -c "CREATE DATABASE goszakupki ENCODING 'UTF8';"
```

### 5. Настроить пароль БД

В файле `shared/config.py` указать пароль пользователя `postgres`.

### 6. Инициализировать таблицы

```bash
python -c "from shared.database import db; db.init_db()"
```

## Использование

### Запуск отдельных модулей

```bash
python -m goszakupki.run      # Госзакупки (поиск AI-контрактов)
python -m hackathons.run      # Хакатоны (сбор с Kaggle)
python -m news.run            # Новости (Хабр, ТАСС, Интерфакс)
python -m shared.import_data  # Импорт всех JSON в БД
python -m shared.view_db      # Просмотр содержимого БД
```

### Планировщик

```bash
python run_all.py
```

Расписание по умолчанию:

| Задача | Период |
|--------|--------|
| Госзакупки | Раз в день (03:00) |
| Хакатоны | Раз в день (04:00) |
| Новости | Каждый час |
| Импорт в БД | Раз в день (05:00) |

## Источники данных

| Модуль | Источник | Тип |
|--------|----------|-----|
| Госзакупки | Clearspending API | REST API |
| Хакатоны | Kaggle API | REST API |
| Новости | Хабр, ТАСС, Интерфакс | RSS |

## База данных

PostgreSQL, 5 таблиц:

| Таблица | Содержимое |
|---------|------------|
| contracts | Госконтракты |
| news | Новости |
| hackathons | Хакатоны |
| ai_insights | Найденные AI-кейсы (аналитика) |
| analytics_log | Логи аналитического модуля |

## Фильтры

### Госзакупки

- Поиск по 12 AI-ключевым словам
- Исключение книг (ОКПД2 58.11.19.000)

### Хакатоны

- Категории: Featured, Research, Hackathons, Simulations
- Отсев игровых и фановых соревнований

### Новости

- Без фильтрации, сохраняются все для последующего анализа