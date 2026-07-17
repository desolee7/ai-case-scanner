"""Точка входа аналитического модуля"""
from analytics.analyzer import AIAnalyzer


def main():
    print("=" * 50)
    print("АНАЛИТИЧЕСКИЙ МОДУЛЬ")
    print("Поиск AI-кейсов")
    print("=" * 50)
    
    analyzer = AIAnalyzer()
    
    print("\n--- ХАКАТОНЫ ---")
    analyzer.analyze_hackathons()
    
    print("\n--- НОВОСТИ ---")
    analyzer.analyze_news()
    
    print("\n--- КОНТРАКТЫ ---")
    analyzer.analyze_contracts(limit=20)


if __name__ == '__main__':
    main()