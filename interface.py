"""
Интерфейс управления модулями.
"""
import subprocess
import sys
import json
from datetime import datetime
from pathlib import Path
from shared.database import db
from sqlalchemy import text


def run_module(module):
    print(f"\n{'='*50}")
    subprocess.run([sys.executable, '-m', module])
    input("\nНажмите Enter для продолжения...")


def show_insights():
    print("\n" + "=" * 50)
    print("AI-КЕЙСЫ")
    print("=" * 50)
    s = db.get_session()
    
    # Новые
    new_rows = s.execute(text(
        "SELECT source_type, title, confidence_score, potential_ai_solution "
        "FROM ai_insights WHERE status = 'new' "
        "ORDER BY confidence_score DESC"
    )).fetchall()
    
    if new_rows:
        print("\n--- НОВЫЕ ---")
        for i, r in enumerate(new_rows, 1):
            print(f"\n{i}. [{r[0]}] {r[1]}")
            print(f"   Уверенность: {r[2]}")
            print(f"   Решение: {r[3][:200]}")
    else:
        print("\nНовых AI-кейсов нет")
    
    # Старые
    old_rows = s.execute(text(
        "SELECT source_type, title, confidence_score, potential_ai_solution "
        "FROM ai_insights WHERE status != 'new' "
        "ORDER BY created_at DESC LIMIT 10"
    )).fetchall()
    
    if old_rows:
        print("\n--- ОБРАБОТАННЫЕ (последние 10) ---")
        for i, r in enumerate(old_rows, 1):
            print(f"\n{i}. [{r[0]}] {r[1]}")
            print(f"   Уверенность: {r[2]}")
    
    s.close()


def export_table(table_name):
    s = db.get_session()
    rows = s.execute(text(f"SELECT * FROM {table_name}")).fetchall()
    columns = s.execute(text(
        f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}'"
    )).fetchall()
    
    data = []
    for row in rows:
        item = {}
        for i, col in enumerate(columns):
            val = row[i]
            if isinstance(val, datetime):
                val = val.isoformat()
            item[col[0]] = val
        data.append(item)
    
    export_dir = Path('exports')
    export_dir.mkdir(exist_ok=True)
    filename = f"{table_name}_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.json"
    filepath = export_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Экспортировано {len(data)} записей в {filepath}")
    s.close()


def export_menu():
    print("\n" + "=" * 50)
    print("ЭКСПОРТ ТАБЛИЦЫ")
    print("=" * 50)
    print("1. contracts")
    print("2. news")
    print("3. hackathons")
    print("4. ai_insights")
    print("5. analytics_log")
    print("0. Назад")
    
    choice = input("\nВыберите таблицу: ").strip()
    
    tables = {
        '1': 'contracts',
        '2': 'news',
        '3': 'hackathons',
        '4': 'ai_insights',
        '5': 'analytics_log',
    }
    
    if choice in tables:
        export_table(tables[choice])
        input("\nНажмите Enter...")
    elif choice != '0':
        print("Неверный выбор")


def main():
    while True:
        print("\n" + "=" * 50)
        print("AUTOPARSING — УПРАВЛЕНИЕ")
        print("=" * 50)
        print("1. Парсер госзакупок")
        print("2. Парсер хакатонов")
        print("3. Парсер новостей")
        print("4. Импорт данных в БД")
        print("5. Анализ новых данных (LLM)")
        print("6. Просмотр БД")
        print("7. AI-кейсы")
        print("8. Экспорт таблицы в JSON")
        print("9. Все модули сбора")
        print("0. Выход")
        
        choice = input("\nВыберите действие: ").strip()
        
        if choice == '1':
            run_module('goszakupki.run')
        elif choice == '2':
            run_module('hackathons.run')
        elif choice == '3':
            run_module('news.run')
        elif choice == '4':
            run_module('shared.import_data')
        elif choice == '5':
            run_module('analytics.run')
        elif choice == '6':
            run_module('shared.view_db')
        elif choice == '7':
            show_insights()
            input("\nНажмите Enter для продолжения...")
        elif choice == '8':
            export_menu()
        elif choice == '9':
            print("\nЗапуск всех модулей сбора...")
            run_module('goszakupki.run')
            run_module('hackathons.run')
            run_module('news.run')
        elif choice == '0':
            print("Выход")
            break
        else:
            print("Неверный выбор")


if __name__ == '__main__':
    main()