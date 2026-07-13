"""Просмотр содержимого БД"""
from shared.database import db
from sqlalchemy import text

s = db.get_session()

print('=' * 60)
print('ТАБЛИЦЫ И ИХ СОДЕРЖИМОЕ')
print('=' * 60)

# Contracts
print('\n--- CONTRACTS (госконтракты) ---')
print(f'Всего: {s.execute(text("SELECT count(*) FROM contracts")).scalar()}')
for row in s.execute(text('SELECT regnum, price, sign_date, customer_inn, description FROM contracts LIMIT 3')):
    print(f'  regnum: {row[0]} | price: {row[1]:,.0f} RUB | date: {row[2]}')
    print(f'  customer_inn: {row[3]}')
    print(f'  description: {row[4][:100]}')
    print()

# News
print('--- NEWS (новости) ---')
print(f'Всего: {s.execute(text("SELECT count(*) FROM news")).scalar()}')
for row in s.execute(text('SELECT title, source, date FROM news LIMIT 3')):
    print(f'  [{row[1]}] {row[0][:80]}')
    print(f'  date: {row[2]}')
    print()

# Hackathons
print('--- HACKATHONS (хакатоны) ---')
print(f'Всего: {s.execute(text("SELECT count(*) FROM hackathons")).scalar()}')
for row in s.execute(text('SELECT title, organizer, end_date, topics FROM hackathons')):
    print(f'  {row[0]}')
    print(f'  organizer: {row[1]} | deadline: {row[2]}')
    print(f'  topics: {row[3]}')
    print()

s.close()