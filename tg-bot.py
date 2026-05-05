import telebot
from telebot import types
import sqlite3
import time


bot = telebot.TeleBot('')
bot1 = telebot.TeleBot('')



user_orders = {}
bot_message_storage = {}



def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_cooldowns (
            user_id INTEGER PRIMARY KEY,
            last_order INTEGER
        )
    ''')
    conn.commit()
    conn.close()



def can_make_order(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('SELECT last_order FROM user_cooldowns WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    if result is None:
        return True, 0
    else:
        last_order = result[0]
        current_time = int(time.time())
        cooldown = 10 * 60
        time_passed = current_time - last_order

        if time_passed >= cooldown:
            return True, 0
        else:
            time_left = cooldown - time_passed
            return False, time_left



def update_order_time(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    current_time = int(time.time())

    cursor.execute('''
        INSERT OR REPLACE INTO user_cooldowns (user_id, last_order)
        VALUES (?, ?)
    ''', (user_id, current_time))

    conn.commit()
    conn.close()



def save_bot_message(user_id, chat_id, message_id):
    key = f"{user_id}_{chat_id}"
    if key not in bot_message_storage:
        bot_message_storage[key] = []
    bot_message_storage[key].append(message_id)


def delete_all_bot_messages(user_id, chat_id):
    
    key = f"{user_id}_{chat_id}"
    if key in bot_message_storage:
        for message_id in bot_message_storage[key]:
            try:
                bot.delete_message(chat_id, message_id)
            except Exception as e:
                print(f"Не удалось удалить сообщение {message_id}: {e}")
        # Очищаем хранилище
        del bot_message_storage[key]


def send_and_save_message(chat_id, text, user_id=None, reply_markup=None):
    msg = bot.send_message(chat_id, text, reply_markup=reply_markup)
    if user_id:
        save_bot_message(user_id, chat_id, msg.message_id)
    return msg


def edit_and_save_message(chat_id, message_id, text, user_id=None, reply_markup=None):
    msg = bot.edit_message_text(text, chat_id, message_id, reply_markup=reply_markup)
    if user_id:
        save_bot_message(user_id, chat_id, message_id)
    return msg



init_db()


@bot.message_handler(commands=['start'])
def start(message):
    delete_all_bot_messages(message.from_user.id, message.chat.id)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('сделать заказ')
    markup.row(btn1)

    send_and_save_message(message.chat.id, 'Привет я тг бот', message.from_user.id)
    photo_url = 'https://i.pinimg.com/originals/8c/e3/a9/8ce3a9b750dedc374e04be2813f48d05.jpg'


    photo_msg = bot.send_photo(message.chat.id, photo_url, reply_markup=markup)
    save_bot_message(message.from_user.id, message.chat.id, photo_msg.message_id)


@bot.message_handler(func=lambda message: True)
def on_click(message):
    if message.text == "сделать заказ":
        user_id = message.chat.id
        can_order, time_left = can_make_order(user_id)

        if can_order:
            user_orders[message.chat.id] = []

            markup = types.InlineKeyboardMarkup(row_width=2)
            item1 = types.InlineKeyboardButton('напитки', callback_data='drinks')
            item2 = types.InlineKeyboardButton('блюда', callback_data='dishes')
            item3 = types.InlineKeyboardButton('мороженое', callback_data='ice_cream')
            item4 = types.InlineKeyboardButton('десерты', callback_data='dessert')
            markup.add(item1, item2, item3, item4)

            send_and_save_message(message.chat.id, 'Выберите категорию:', message.from_user.id, reply_markup=markup)

        else:
            minutes_left = time_left // 60
            seconds_left = time_left % 60
            bot.send_message(message.chat.id,
                             f' Вы не можете сделать заказ сейчас. Подождите еще {minutes_left} минут {seconds_left} секунд.')

    else:
        send_and_save_message(message.chat.id, 'такой функция нета', message.from_user.id)


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    prices = {
        'Кофе': 50,
        'Чай': 35,
        'Сок': 40,
        'Газировка': 45,
        'чебурек': 80,
        'шаурма': 120,
        'шашлык': 200,
        'хачапури': 90,
        'пломбир с шоколадной посыпкой': 60,
        'пломбир': 50,
        'с фисташками': 70,
        'с шоколадом': 65,
        'пирожное картошка': 45,
        'мини торт': 150,
        'кекс': 40,
        'блины': 85
    }

    if call.data == "drinks":
        markup = types.InlineKeyboardMarkup(row_width=2)
        drinks = ['Кофе', 'Чай', 'Сок', 'Газировка']
        for drink in drinks:
            markup.add(types.InlineKeyboardButton(drink, callback_data=f'product_{drink}'))
        edit_and_save_message(call.message.chat.id, call.message.message_id, 'Выберите напиток:', call.from_user.id,
                              reply_markup=markup)

    elif call.data == "dishes":
        markup = types.InlineKeyboardMarkup(row_width=2)
        dishes = ['чебурек', 'шаурма', 'шашлык', 'хачапури']
        for dish in dishes:
            markup.add(types.InlineKeyboardButton(dish, callback_data=f'product_{dish}'))
        edit_and_save_message(call.message.chat.id, call.message.message_id, 'Выберите блюдо:', call.from_user.id,
                              reply_markup=markup)

    elif call.data == "ice_cream":
        markup = types.InlineKeyboardMarkup(row_width=2)
        ice_creams = ['пломбир с шоколадной посыпкой', 'пломбир', 'с фисташками', 'с шоколадом']
        for ice_cream in ice_creams:
            markup.add(types.InlineKeyboardButton(ice_cream, callback_data=f'product_{ice_cream}'))
        edit_and_save_message(call.message.chat.id, call.message.message_id, 'Выберите мороженое:', call.from_user.id,
                              reply_markup=markup)

    elif call.data == "dessert":
        markup = types.InlineKeyboardMarkup(row_width=2)
        desserts = ['пирожное картошка', 'мини торт', 'кекс', 'блины']
        for dessert in desserts:
            markup.add(types.InlineKeyboardButton(dessert, callback_data=f'product_{dessert}'))
        edit_and_save_message(call.message.chat.id, call.message.message_id, 'Выберите десерт:', call.from_user.id,
                              reply_markup=markup)

    elif call.data.startswith('product_'):
        product_name = call.data.replace('product_', '')
        price = prices.get(product_name, 0)

        if call.message.chat.id not in user_orders:
            user_orders[call.message.chat.id] = []
        user_orders[call.message.chat.id].append((product_name, price))

        markup = types.InlineKeyboardMarkup(row_width=2)
        btn100 = types.InlineKeyboardButton('да', callback_data='continue_yes')
        btn200 = types.InlineKeyboardButton('нет', callback_data='continue_no')
        markup.add(btn100, btn200)

        send_and_save_message(call.message.chat.id,
                              f'Вы выбрали: {product_name}\nЦена: {price} рублей\n\nХотите заказать что-то еще?',
                              call.from_user.id, reply_markup=markup)

        bot.answer_callback_query(call.id, f"Вы выбрали {product_name} за {price} рублей")

    elif call.data == 'continue_yes':
        markup = types.InlineKeyboardMarkup(row_width=2)
        item1 = types.InlineKeyboardButton('напитки', callback_data='drinks')
        item2 = types.InlineKeyboardButton('блюда', callback_data='dishes')
        item3 = types.InlineKeyboardButton('мороженое', callback_data='ice_cream')
        item4 = types.InlineKeyboardButton('десерты', callback_data='dessert')
        markup.add(item1, item2, item3, item4)
        edit_and_save_message(call.message.chat.id, call.message.message_id, 'Выберите категорию:', call.from_user.id,
                              reply_markup=markup)

    elif call.data == 'continue_no':
        if call.message.chat.id in user_orders and user_orders[call.message.chat.id]:
            total = sum(price for _, price in user_orders[call.message.chat.id])
            order_details = "\n".join([f"- {item}: {price} руб." for item, price in user_orders[call.message.chat.id]])

            update_order_time(call.message.chat.id)

            delete_all_bot_messages(call.from_user.id, call.message.chat.id)

            final_text = (f' Ваш заказ принят!\n\n'
                          f'Детали заказа:\n{order_details}\n\n'
                          f' Итого: {total} рублей\n\n'
                          f' Оплатите на номер 88005553535!\n\n'
                          f' Следующий заказ будет доступен через 10 минут')

            bot.send_message(call.message.chat.id, final_text)

            bot1.send_message(call.message.chat.id,
                              f' Новый заказ!\n\nДетали:\n{order_details}\n\n Итого: {total} рублей')

            
            user_orders[call.message.chat.id] = []

        else:
            delete_all_bot_messages(call.from_user.id, call.message.chat.id)
            bot.send_message(call.message.chat.id, ' Ваш заказ пуст.')


bot.polling(none_stop=True)
