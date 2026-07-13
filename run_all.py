"""
Планировщик запуска всех модулей сбора данных.
"""
import time
import schedule
import subprocess
import sys
from datetime import datetime


def run_goszakupki():
    print(f"\n[{datetime.now()}] Запуск: госзакупки")
    subprocess.run([sys.executable, '-m', 'goszakupki.run'])


def run_hackathons():
    print(f"\n[{datetime.now()}] Запуск: хакатоны")
    subprocess.run([sys.executable, '-m', 'hackathons.run'])


def run_news():
    print(f"\n[{datetime.now()}] Запуск: новости")
    subprocess.run([sys.executable, '-m', 'news.run'])


def import_to_db():
    print(f"\n[{datetime.now()}] Импорт данных в БД")
    subprocess.run([sys.executable, '-m', 'shared.import_data'])


def main():
    print("=" * 50)
    print("ПЛАНИРОВЩИК СБОРА ДАННЫХ")
    print("=" * 50)
    
    # Госзакупки — раз в день (лимит API 100 запросов)
    schedule.every().day.at("03:00").do(run_goszakupki)
    
    # Хакатоны — раз в день
    schedule.every().day.at("04:00").do(run_hackathons)
    
    # Новости — каждый час
    schedule.every().hour.do(run_news)
    
    # Импорт в БД — раз в день после всех сборов
    schedule.every().day.at("05:00").do(import_to_db)
    
    print("\nРасписание:")
    print("  03:00 — госзакупки")
    print("  04:00 — хакатоны")
    print("  05:00 — импорт в БД")
    print("  каждый час — новости")
    print("\nОжидание...")
    
    # Первый запуск сразу
    run_news()
    run_hackathons()
    
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == '__main__':
    main()