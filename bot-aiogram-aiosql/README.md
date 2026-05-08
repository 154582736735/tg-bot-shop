# Telegram бот для сбора идей (aiogram)

Telegram бот для сбора идей Telegram-ботов. Пользователи оставляют заявки, администратор их просматривает.

## Технологии

- Python 3.10+
- aiogram 3.x
- aiosqlite
- FSM

## Установка и запуск

1. Установите зависимости:
   pip install -r requirements.txt

2. Создайте config.py:
   TOKEN = "ваш_токен"
   ADMIN_ID = ваш_telegram_id   # узнать у @userinfobot

3. Запустите:
   python run.py

## Команды

Пользователь:
/start — приветствие
/idea — оставить идею

Админ:
/bots — просмотр идей
