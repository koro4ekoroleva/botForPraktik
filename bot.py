import telebot
import mysql.connector as ms
from mysql.connector import Error
import logging
from io import BytesIO

bot = telebot.TeleBot('6782288362:AAGOEAPSZQc-2MzwnBDcRfzpg5vX9YhGk4k', skip_pending=True)
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


@bot.callback_query_handler(func=lambda callback: callback.data == 'choice_wear')  #callback.data возвращает идентификаторы кнопок
def category_callback(callback):
    query = 'SELECT * FROM category'

    # В переменной row записывается результат работы запроса
    row = connect(query)

    markup = telebot.types.InlineKeyboardMarkup(row_width=3)
    for i in row:
        # Каждый результат запроса заносим как кнопку
        markup.add(telebot.types.InlineKeyboardButton(text=i[1], callback_data=f'category{i[0]}'))
    bot.send_message(callback.message.chat.id, text='Выберите категорию товара:', reply_markup=markup)

@bot.callback_query_handler(func=lambda callback: callback.data == 'where_order')
def where_order_callback(callback):
    bot.send_message(callback.message.chat.id, text='Ваш заказ был отдан на нужды голодающих африканских детей!'
                                                    '\n/start - начать сначала', callback_data='order')


@bot.callback_query_handler(func=lambda callback: 'category' in callback.data)
def products_callback(callback, viewed_product = 0):
    category = callback.data[8:]
    query = (f'SELECT products.products_id, products.product_name, maker.maker_name, maker.maker_country, ' 
             f'products.price, products.picture FROM products JOIN maker ON products.maker_id = maker.maker_id '
             f'WHERE products.category_id = {category}')
    row = connect(query)
    print(viewed_product)
    if viewed_product < 0:
        viewed_product = 0
    pictures = list()
    for i in range(len(row)):
        pictures.append([row[i][0], row[i][5]])
    text_for_message = (f'{row[viewed_product][1]}\nПроизводитель: {row[viewed_product][2]}'
                        f'\nСтрана производства: {row[viewed_product][3]}'
                        f'\nСтрана производства: {row[viewed_product][3]}'
                        f'\n\n*Цена: {row[viewed_product][4]} ₽*')
    photo_now = BytesIO(pictures[viewed_product][1])

    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    product_before = telebot.types.InlineKeyboardButton(text='\U00002B05', callback_data='product_before')
    cart = telebot.types.InlineKeyboardButton(text='В корзину\U0001F6D2', callback_data='cart')
    product_after = telebot.types.InlineKeyboardButton(text='\U000027A1', callback_data='product_after')
    markup.add(product_before, cart, product_after)
    bot.send_photo(callback.message.chat.id, caption=text_for_message, photo=photo_now, parse_mode='Markdown',
                   reply_markup = markup)


@bot.callback_query_handler(func=lambda callback: callback.data == 'product_before' or callback.data == 'product_after')
def products_callback_next(callback):
    if callback.data == 'product_before':
        products_callback(callback, viewed_product = +1)
    elif callback.data == 'product_after':
        products_callback(callback, viewed_product=-1)

@bot.message_handler(content_types=["text"])
def what(message):
    bot.send_message(message.chat.id, text='Я не понимаю \U0001F625 ')

if __name__ == '__main__':
     bot.infinity_polling()