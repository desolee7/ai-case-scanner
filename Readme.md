# Система автоматического сбора и анализа данных для выявления AI-кейсов в госзакупках, хакатонах и новостях

## Структура проекта

```
Autoparsing/
├── analytics/               # Аналитический модуль
│   ├── config.py            # Настройки LLM
│   ├── llm_client.py        # Клиент к модели (Ollama)
│   ├── analyzer.py          # Логика анализа и сохранения
│   └── run.py               # Точка входа
├── shared/
│   ├── config.py            # Общие настройки
│   ├── models.py            # Модели БД (SQLAlchemy)
│   ├── database.py          # Работа с PostgreSQL
│   ├── import_data.py       # Импорт JSON в БД
│   └── view_db.py           # Просмотр содержимого БД
├── goszakupki/
│   ├── api_client.py        # Клиент Clearspending API
│   ├── download_documents.py  # Скачивание файлов
│   ├── filters.py           # Ключевые слова и фильтры
│   ├── config.py            # Настройки модуля
│   ├── run.py               # Точка входа
│   └── data/                # Сохранённые JSON и документы
├── hackathons/
│   ├── kaggle_scraper.py    # Сбор с Kaggle API
│   ├── parser.py            # Фильтрация и нормализация
│   ├── filters.py           # Ключевые слова
│   ├── config.py            # Настройки модуля
│   ├── run.py               # Точка входа
│   └── data/                # Сохранённые JSON
├── news/
│   ├── rss_parser.py        # Парсер RSS-лент
│   ├── config.py            # Настройки модуля
│   ├── run.py               # Точка входа
│   └── data/                # Сохранённые JSON
├── exports/                 # Экспортированные JSON
├── interface.py             # Интерфейс управления
├── run_all.py               # Планировщик
├── requirements.txt         # Зависимости
└── README.md                
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

### 7. Установить Ollama и скачать модель

Скачать с https://ollama.com/download/windows и установить.

```bash
ollama pull deepseek-r1:8b
```

### 8. Настроить Kaggle API

Получить `kaggle.json` на https://www.kaggle.com/settings и поместить в `C:\Users\Name\.kaggle\`.

## Использование

### Интерфейс управления

```bash
python interface.py
```

| Пункт | Действие | Описание |
|-------|----------|----------|
| 1 | Парсер госзакупок | Поиск контрактов через Clearspending API |
| 2 | Парсер хакатонов | Сбор с Kaggle API |
| 3 | Парсер новостей | Хабр, ТАСС, Интерфакс |
| 4 | Импорт данных в БД | Перенос JSON в PostgreSQL |
| 5 | Анализ новых данных (LLM) | Поиск AI-кейсов через DeepSeek R1 |
| 6 | Просмотр БД | Статистика и примеры записей |
| 7 | AI-кейсы | Просмотр найденных кейсов (новые/старые) |
| 8 | Экспорт таблицы в JSON | Выбор таблицы: contracts, news, hackathons, ai_insights, analytics_log |
| 9 | Все модули сбора | Запуск госзакупок + хакатонов + новостей |
| 0 | Выход | — |

### Запуск отдельных модулей

```bash
python -m goszakupki.run      # Госзакупки
python -m hackathons.run      # Хакатоны
python -m news.run            # Новости
python -m analytics.run       # Анализ через LLM
python -m shared.import_data  # Импорт в БД
python -m shared.view_db      # Просмотр БД
```

### Планировщик

```bash
python run_all.py
```

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
| ai_insights | AI-кейсы |
| analytics_log | Логи аналитики |

## Аналитический модуль

Локальная LLM через Ollama:
- Модель: `deepseek-r1:8b`
- Статусы инсайтов: `new` (свежие) / `old` (предыдущие)
- Анализируются только записи со статусом `new`
- После анализа статус источника меняется на `analyzed`

## Фильтры

### Госзакупки

- Поиск по 12 AI-ключевым словам
- Исключение книг (ОКПД2 58.11.19.000)

### Хакатоны

- Категории: Featured, Research, Hackathons, Simulations
- Отсев игровых и фановых соревнований

### Новости

- Без фильтрации, сохраняются все для последующего анализа

## Экспорт

Через интерфейс (пункт 8) можно экспортировать любую таблицу в JSON. Файлы сохраняются в папку `exports/`.