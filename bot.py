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

    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    choise_wear = telebot.types.InlineKeyboardButton(text="Выбрать товар", callback_data='choise_wear')
    where_order = telebot.types.InlineKeyboardButton(text="Узнать статус заказа", callback_data='where_order')
    markup.add(choise_wear, where_order)
    bot.send_message(message.chat.id, text='Выберите дальнейшие действия', reply_markup=markup)

def print_categories(message):
    query = 'SELECT category_name FROM category'  #Запрос к бд на вывод названий всех категорий товаров

    #В переменной row записывается результат работы запроса
    row = connect(query)

    '''send_message - метод, отправляющий сообщение.
            message.chat.id - айдишник чата, из которого пришло сообщение, на которое надо ответить.
            message.text - текст присланного боту сообщения'''

    bot.send_message(message.chat.id, text='В нашем магазине есть следующие категории товаров:')
    for i in row:
        bot.send_message(message.chat.id, i[0])

@bot.callback_query_handler(func=lambda callback: callback.data)
def start_callback(callback):
    if callback.data == 'choise_wear' :
        print_categories(callback.message)



if __name__ == '__main__':
     bot.infinity_polling()