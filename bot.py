import telebot
import mysql.connector as ms
from mysql.connector import Error
import logging
from io import BytesIO
import re
import random

bot = telebot.TeleBot('7397593743:AAGJXf5jUKLO7EsoDTf2W8nVNmj68RbBnTs', skip_pending=True)
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

#Подключение к бд

def connect(query):
    results = []
    try:
        conn = ms.connect(user='root', password='23072003', host='127.0.0.1', database='shop_wear1')

        if not conn.is_connected():
            print('Connected to MySQL database')

        cursor = conn.cursor()
        cursor.execute(query)

        row = cursor.fetchone()
        while row is not None:
            results.append(row)
            row = cursor.fetchone()
    except Error as e:
        print(e)
    return results

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, text='Привет! Я помогу тебе с покупкой в нашем магазине!')

    markup = telebot.types.InlineKeyboardMarkup(row_width=1)  # Это для кнопок под сообщ-м бота (row_width кол-во строк)

    '''В перем-х choise_wear и where_order задаются сами кнопочки
    callback_data - это идентификатор, по которому можно отследить, что эта кнопка нажата (см. ф-ю start_callback)'''
    choice_wear = telebot.types.InlineKeyboardButton(text="Выбрать товар", callback_data='choice_wear')
    where_order = telebot.types.InlineKeyboardButton(text="Узнать статус заказа", callback_data='where_order')

    markup.add(choice_wear, where_order)  #Добавим кнопочки в контейнер для них
    bot.send_message(message.chat.id, text='Выберите дальнейшие действия', reply_markup=markup)  #reply_markup - кнопки


@bot.callback_query_handler(func=lambda callback: callback.data =='where_order')
def check_order(callback):
    bot.send_message(callback.message.chat.id, text="Пожалуйста, введите номер вашего заказа в формате 'Заказ 12345678'")
    bot.register_next_step_handler(callback.message, handle_order_id)

# Функция для обработки ввода номера заказа
@bot.message_handler(func=lambda message: message.text.lower().startswith('заказ'))
def handle_order_id(message):
    order_id_match = re.search(r'заказ\s*[0-9]', message.text.lower())
    if order_id_match:
        order_id = message.text[-8:]
        user_id = message.from_user.id

        # Замените функцию connect на ваш метод для выполнения SQL-запроса и получения результатов
        query = f"SELECT * FROM orders WHERE orders_id = {order_id}"
        rows = connect(query)  # Предполагается, что connect возвращает список строк

        if rows:
            row = rows[0]
            if row[1] == user_id:
                bot.send_message(chat_id=message.chat.id, text=f"Статус вашего заказа: {row[2]}")
            else:
                bot.send_message(chat_id=message.chat.id, text="Заказ был сделан с другого аккаунта. "
                                                               "Попробуйте написать с него!")
        else:
            bot.send_message(chat_id=message.chat.id,
                             text="Заказ не найден. Возможно, Вы ввели некорректный номер заказа. "
                                  "Пожалуйста, попробуйте еще раз!")
    else:
        bot.send_message(chat_id=message.chat.id,
                         text="Пожалуйста, введите корректный номер заказа в формате 'Заказ 12345678'.")


viewed_product = 0
category = 0

@bot.callback_query_handler(func=lambda callback: callback.data == 'choice_wear')  #callback.data возвращает идентификаторы кнопок
def category_callback(callback):
    global viewed_product, category
    query = 'SELECT * FROM category'
    # В переменной row записывается результат работы запроса
    row = connect(query)
    markup = telebot.types.InlineKeyboardMarkup(row_width=3)
    for i in row:
        # Каждый результат запроса заносим как кнопку
        markup.add(telebot.types.InlineKeyboardButton(text=i[1], callback_data=f'category{i[0]}'))

    viewed_product = 0
    category = 0

    bot.send_message(callback.message.chat.id, text='Выберите категорию товара:', reply_markup=markup)

# @bot.callback_query_handler(func=lambda callback: callback.data == 'where_order')
# def where_order_callback(callback):
#     bot.send_message(callback.message.chat.id, text='Ваш заказ был отдан на нужды голодающих африканских детей!'
#                                                     '\n/start - начать сначала')


@bot.callback_query_handler(func=lambda callback: 'category' in callback.data)
def products_callback(callback):
    global viewed_product, row, category
    try:
        int(callback.data[8:])
        category = callback.data[8:]
    except:
        pass
    if viewed_product == 0 :
        query = (f'SELECT products.products_id, products.product_name, maker.maker_name, maker.maker_country, '
                 f'products.price, products.picture FROM products JOIN maker ON products.maker_id = maker.maker_id '
                 f'WHERE products.category_id = {category}')
        row = connect(query)
    elif viewed_product < 0:
        viewed_product = 0
    elif viewed_product == len(row):
        viewed_product = len(row) - 1
    pictures = list()
    for i in range(len(row)):
        pictures.append([row[i][0], row[i][5]])
    text_for_message = (f'{row[viewed_product][1]}\nПроизводитель: {row[viewed_product][2]}'
                        f'\nСтрана производства: {row[viewed_product][3]}'
                        f'\n\n*Цена: {row[viewed_product][4]} ₽*')
    photo_now = BytesIO(pictures[viewed_product][1])

    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    product_before = telebot.types.InlineKeyboardButton(text='\U00002B05', callback_data='product_before')
    cart = telebot.types.InlineKeyboardButton(text='Купить\U0001F6D2\u2002', callback_data='cart')
    product_after = telebot.types.InlineKeyboardButton(text='\U000027A1', callback_data='product_after')
    markup.add(product_before, product_after)
    markup.add(cart)
    bot.send_photo(callback.message.chat.id, caption=text_for_message, photo=photo_now, parse_mode='Markdown',
                   reply_markup = markup)


@bot.callback_query_handler(func=lambda callback: callback.data == 'product_before' or callback.data == 'product_after')
def products_callback_next(callback):
    global viewed_product
    if callback.data == 'product_before':
        viewed_product -= 1
    elif callback.data == 'product_after':
        viewed_product += 1
    products_callback(callback)

products_id = 1
@bot.callback_query_handler(func=lambda callback: callback.data == 'cart')
def cart_callback(callback):
    global clothes_id
    products_id = row[viewed_product][0]
    query = f'SELECT * FROM new_storage WHERE clothes_id DIV 100 = {products_id}'
    clothes_id = connect(query)
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    if clothes_id:
        #text_for_message = f"Вы выбрали продукт, для него доступны размеры: {clothes_id}"
        for g in range(len(clothes_id)):
            text_for_message =telebot.types.InlineKeyboardButton (f"Для размера {clothes_id[g][0]%100} доступно {clothes_id[g][1]}", callback_data=f'orderB{clothes_id[g]}')
            markup.add(text_for_message)
        bot.send_message(callback.message.chat.id,text="Выберите размер:", reply_markup = markup)
    else:
        bot.send_message(callback.message.chat.id, "Выбранный продукт недоступен")


@bot.callback_query_handler(func=lambda callback: 'orderB' in callback.data)
def check_order(callback):
    order = callback.data[7:-1].split(', ')

    query = f"SELECT buyer_id FROM buyers WHERE buyer_id = {callback.from_user.id}"
    row = connect(query)
    if len(row) == 0:
        query = (f"INSERT INTO buyers (buyer_id, buyer_name, buyer_phone) "
                 f"VALUES ('{callback.from_user.id}', '{callback.from_user.first_name}', '')")
        row = connect(query)

    order_id = random.randint(10000000, 99999999)
    query = (
        f"INSERT INTO orders (orders_id, buyers_id, orders_state, products_id, sizes_id) "
        f"VALUES ('{order_id}', '{callback.from_user.id}', 'Зарегистрирован', "
        f"'{int(order[0]) // 100}', '{int(order[0])}')"
    )
    try:
        row = connect(query)
    except:
        while len(row) == 0:
            order_id = random.randint(10000000, 99999999)
            query = (
                f"INSERT INTO orders (orders_id, buyers_id, orders_state, products_id, sizes_id) "
                f"VALUES ('{order_id}', '{callback.from_user.id}', 'Зарегистрирован', "
                f"'{int(order[0]) // 100}', '{int(order[0])}')"
            )
            row = connect(query)
    print(query)
    bot.send_message(callback.message.chat.id, text=f"Ваш заказ зарегистрирован под номером {order_id}.\n"
                                                    f"Спасибо за заказ!")


@bot.message_handler(content_types=["text"])
def what(message):
    bot.send_message(message.chat.id, text='Я не понимаю \U0001F625 ')

if __name__ == '__main__':
     bot.infinity_polling()