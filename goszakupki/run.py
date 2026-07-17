"""
Парсер госзакупок: поиск -> метаданные -> сохранение в JSON.
"""
import json
from datetime import datetime
from pathlib import Path
from goszakupki.api_client import ClearspendingClient
from goszakupki.filters import SEARCH_QUERIES, DATE_FROM, DATE_TO, EXCLUDE_OKPD2


def should_exclude(contract: dict) -> bool:
    for p in contract.get('products', []):
        code = p.get('OKPD2', {}).get('code', '')
        for ex in EXCLUDE_OKPD2:
            if code.startswith(ex):
                return True

    desc = ' '.join(p.get('name', '') for p in contract.get('products', [])).lower()
    book_words = ['книга', 'учебник', 'учебное пособие', 'словарь', 'энциклопедия']
    for word in book_words:
        if word in desc:
            return True

    return False


def extract_metadata(contract: dict) -> dict:
    return {
        'regnum': contract.get('regNum', ''),
        'price': contract.get('price', 0),
        'sign_date': contract.get('signDate', '')[:10] if contract.get('signDate') else '',
        'customer_name': contract.get('customer', {}).get('fullName', ''),
        'customer_inn': contract.get('customer', {}).get('inn', ''),
        'supplier_name': contract.get('suppliers', [{}])[0].get('organizationName', '') if contract.get('suppliers') else '',
        'supplier_inn': contract.get('suppliers', [{}])[0].get('inn', '') if contract.get('suppliers') else '',
        'products': [
            {
                'name': p.get('name', ''),
                'okpd2_code': p.get('OKPD2', {}).get('code', ''),
                'okpd2_name': p.get('OKPD2', {}).get('name', ''),
                'price': p.get('price', 0),
            }
            for p in contract.get('products', [])
        ],
        'fz': contract.get('fz', ''),
        'current_stage': contract.get('currentContractStage', ''),
        'region_code': contract.get('regionCode', ''),
        'url': contract.get('contractUrl', ''),
        'matched_query': contract.get('_matched_query', ''),
    }


def main():
    print("=" * 60)
    print("ПАРСЕР ГОСЗАКУПОК")
    print("=" * 60)

    client = ClearspendingClient()

    try:
        contracts = client.search_all_queries(
            keywords=SEARCH_QUERIES,
            date_from=DATE_FROM,
            date_to=DATE_TO
        )

        if not contracts:
            print("Ничего не найдено")
            return

        metadata_list = []
        excluded = 0
        for c in contracts:
            if should_exclude(c):
                excluded += 1
                continue
            metadata_list.append(extract_metadata(c))

        print(f"\nИсключено: {excluded} контрактов")

        if not metadata_list:
            print("После фильтрации ничего не осталось")
            return

        data_dir = Path(__file__).parent / 'data' / 'documents'
        data_dir.mkdir(parents=True, exist_ok=True)

        filename = f"contracts_{len(metadata_list)}items_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.json"
        filepath = data_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(metadata_list, f, ensure_ascii=False, indent=2)

        print(f"Сохранено {len(metadata_list)} контрактов в {filepath}")

        total_price = sum(c['price'] for c in metadata_list if c['price'])
        print(f"Общая сумма: {total_price:,.0f} RUB")

        customers = {}
        for c in metadata_list:
            name = c['customer_name']
            if name:
                customers[name] = customers.get(name, 0) + 1
        top = sorted(customers.items(), key=lambda x: x[1], reverse=True)[:5]
        print("\nТоп заказчиков:")
        for name, count in top:
            print(f"  {name}: {count}")

    finally:
        client.close()


if __name__ == '__main__':
    main()