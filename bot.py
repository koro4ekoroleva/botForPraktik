import telebot
import mysql.connector as ms
from mysql.connector import Error

bot = telebot.TeleBot('6782288362:AAFdSdU_eK0k23dj3bj19i4HisT_2n6Upvw')

#Подключение к бд

def connect(query):
    results = []
    try:
        conn = ms.connect(user='root', password='23072003', host='127.0.0.1', database='shop_wear')

        if not conn.is_connected():
            print('Connected to MySQL database')

        cursor = conn.cursor()
        cursor.execute(query)

        row = cursor.fetchone()
        while row is not None:
            print(row)
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

def print_categories(message):
    query = 'SELECT category_name FROM category'  #Запрос к бд на вывод названий всех категорий товаров

    #В переменной row записывается результат работы запроса
    row = connect(query)

    markup = telebot.types.InlineKeyboardMarkup(row_width=3)
    for i in row:
        #Каждый результат запроса заносим как кнопку
        markup.add(telebot.types.InlineKeyboardButton(text=i[0], callback_data=i[0]))
    bot.send_message(message.chat.id, text='Выберите категорию товара:', reply_markup=markup)


#тут отслеживаются кнопочки "Выбрать товар" и "Узнать статус заказа" (да, по тем идентификаторам)
@bot.callback_query_handler(func=lambda callback: callback.data)  #callback.data возвращает идентификаторы кнопок
def start_callback(callback):
    if callback.data == 'choice_wear':
        print_categories(callback.message)
    elif callback.data == 'where_order':
        #callback.message.chat.id - такой же id, как и раньше, просто спереди пишется callback
        bot.send_message(callback.message.chat.id, 'Ваш заказ был отдан на нужды голодающих африканских детей!\n/start - начать сначала')


@bot.message_handler(content_types=["text"])
def what(message):
    bot.send_message(message.chat.id, text='Я не понимаю \U0001F625 ')

if __name__ == '__main__':
     bot.infinity_polling()