import telebot
import mysql.connector as ms
from mysql.connector import Error

bot = telebot.TeleBot('6782288362:AAFdSdU_eK0k23dj3bj19i4HisT_2n6Upvw')

#Подключение к бд

def connect():
    results = []
    try:
        conn = ms.connect(user='root', password='23072003', host='127.0.0.1', database='shop_wear')

        #Если смогли подключиться, то в консоль выведет Есть контакт
        if conn.is_connected():
            print('Connected to MySQL database')

        #Создадим у соединения с бд объект cursor
        cursor = conn.cursor()
        #Выполним запрос
        cursor.execute('SELECT category_id, category_name FROM category')

        #Метод fetchone выдаёт по очереди строки из результатов запроса или None в случае, если строк не осталось
        row = cursor.fetchone()

        while row is not None:
            print(row)
            results.append(row[1])
            row = cursor.fetchone()
    except Error as e:
        print(e)
    return results


@bot.message_handler(commands=['help', 'start'])  #Это декоратор для того, чтобы бот реагировал на команды типа "/help", "/start"
def print_categories(message):
    #В переменной row записывается результат запроса на вывод всех категорий товаров
    row = connect()

    bot.send_message(message.chat.id, 'В нашем магазине есть следующие категории товаров:')
    for i in row:
        bot.send_message(message.chat.id, i)



'''В этой функции бот примет сообщение, вставит его текст в своё сообщение и пришлёт назад пользователю'''
@bot.message_handler(content_types=["text"])  #Это декоратор для того, чтобы бот принял сообщение и оттправил ответ
def repeat_all_messages(message):
    bot.send_message(message.chat.id, f'Вы написали: {message.text}')
    '''send_message - метод, отправляющий сообщение.
        message.chat.id - айдишник чата, из которого пришло сообщение, на которое надо ответить.
        message.text - текст присланного боту сообщения'''
if __name__ == '__main__':
     bot.infinity_polling()
