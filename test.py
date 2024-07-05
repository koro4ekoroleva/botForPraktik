import telebot
import mysql.connector as ms
from mysql.connector import Error

bot = telebot.TeleBot('6782288362:AAGN7ZJxr8of45Ue6-8s0umzz9oMmXt46bE')

#Подключение к бд

def connect(query):
    results = []  #Сюда в конце функции занесутся результаты запроса
    try:
        conn = ms.connect(user='root', password='23072003', host='127.0.0.1', database='shop_wear1')

        #Если смогли подключиться к бд, то в консоль выведет сообщение
        if not conn.is_connected():
            print('Connected to MySQL database')

        #Создадим у соединения с бд объект cursor. Он выполняет операции с БД
        cursor = conn.cursor()
        #Подадим курсору (cursor) запрос
        cursor.execute(query)

        '''Метод fetchone сохраняет строки результатов запроса в кортеж (неизменяемый список) и выдаёт их по очереди
        Если результатов не останется, fetchone выдаст None.
        Надо требовать от него рез-ты, пока он не вытошнит None вместо результата.'''

        row = cursor.fetchone()  #тут fetchone выдал первый результат запроса
        while row is not None:
            print(row)
            results.append(row)  #Записываем очередной результат в список результатов
            row = cursor.fetchone() # fetchone выдал следующий рез-т (или None. Проверим на следующей итерации цикла)
    except Error as e:
        print(e)
    return results


'''В этой функции бот на команды /help и /start делает запрос в бд и выводит результаты'''
@bot.message_handler(commands=['help', 'start'])  #Это декоратор для того, чтобы бот реагировал на команды типа "/help", "/start"
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



'''В этой функции бот примет сообщение, вставит его текст в своё сообщение и пришлёт назад пользователю'''
@bot.message_handler(content_types=["text"])  #Это декоратор для того, чтобы бот принял сообщение и оттправил ответ
def repeat_all_messages(message):
    bot.send_message(message.chat.id, text=f'Вы написали: {message.text}')
    # print(message.from_user.id)   тут я выводила id пользователя. Пригодится потом при оформлении заказа

if __name__ == '__main__':
     bot.infinity_polling()
