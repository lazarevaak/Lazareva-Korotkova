import schedule
import telebot
import sqlite3
import button
import docx
import os
from datetime import date
from time import sleep
from threading import Thread

bot = telebot.TeleBot('2132142651:AAFFusmPInaOmT5AUJlwU1Uu-3Y2sZfcrD4')

chat_id_director = 1415300064
chat_id_secretary = 2040375134
chat_id_assistant = 777702827

information_for_reference = []
information_for_record = []

conn = sqlite3.connect('бот_для_секретаря.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users (us_id INTEGER UNIQUE, us_name TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS docs (id INTEGER PRIMARY KEY AUTOINCREMENT, doc BLOB)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS news (id INTEGER PRIMARY KEY AUTOINCREMENT, text_new VARCHAR(100))''')
cursor.execute(
    '''CREATE TABLE IF NOT EXISTS records (id INTEGER PRIMARY KEY AUTOINCREMENT, rs TEXT, dt TEXT, tm TEXT)''')


# начало работы чат-бота


@bot.message_handler(commands=['start'])
def welcome(message):  # команда /start
    m = bot.send_message(message.chat.id,
                         "Добро пожаловать!"
                         "\nВас приветствует чат-тот секретаря школы 444!"
                         "\nПредставьтесь, пожалуйста!"
                         "\nНазовите своё настоящее ФИО, так как это очень важно при авторизации",
                         reply_markup=button.del_buttons())
    bot.register_next_step_handler(m, entrance)


# авторизация


def entrance(message):  # авторизация пользователей
    if message.chat.id == chat_id_secretary:  # проверка является ли пользователь секретарем
        secretary_welcome(message)
    elif message.chat.id == chat_id_director:  # проверка является ли пользователь директором
        director_welcome(message)
    elif message.chat.id == chat_id_assistant:  # проверка является ли пользователь администратором
        assistant_welcome(message)
    else:  # проверка является ли пользователь обычным
        user_id = message.chat.id
        name_user = str(message.text)
        user = (user_id, name_user)
        cursor.execute('SELECT us_id FROM users')
        results = cursor.fetchall()
        if len(results) == 0:  # проверка наличия пользователя в базе данных
            cursor.execute('INSERT INTO users (us_id, us_name) VALUES (?, ?)', user)
            conn.commit()
        elif user_id not in results[0]:
            cursor.execute('INSERT INTO users (us_id, us_name) VALUES (?, ?)', user)
            conn.commit()
        functions_user(message)


# директор


def director_welcome(message):  # приветствие с директором
    bot.send_message(chat_id_director,
                     "Успешный вход в систему директора!",
                     parse_mode='html')
    director_entrance(message)


def director_entrance(message):  # выбор дня для просмотра записи к директору
    bot.send_message(chat_id_director,
                     "\nНа какой день Вы хотите посмотреть записи?",
                     parse_mode='html')
    director_function(message)


def director_function(message):  # получение дня от директора, на который он хочет посмотреть записи
    m = bot.send_message(chat_id_director,
                         text="Корректный ответ:\n22.01.2022")
    bot.register_next_step_handler(m, date_of_recording_analysis)


def date_of_recording_analysis(message):  # вывод записей на выбранный директором день
    data = list()
    data.append(message.text)
    cursor.execute('SELECT * FROM records WHERE dt = ? ', data)
    results = cursor.fetchall()
    if not results:  # нет записей
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        m = bot.send_message(chat_id_director,
                             text="Нет записи на этот день",
                             reply_markup=markup)
        bot.register_next_step_handler(m, director_entrance)
    else:  # есть записи
        results.sort(key=sorting)
        n = 0
        for i in results:  # вывод записей на выбранный день
            n += 1
            bot.send_message(chat_id_director,
                             str(n) + ') Дата: ' + data[0] + '\n    Время: ' + str(i[3]) + '\n    Причина: ' + str(i[1]),
                             parse_mode='html')
        markup = button.data_analysis_markup()  # узнаем нужно ли удалить запись
        m = bot.send_message(chat_id_director,
                             text="Хотите отменить запись?",
                             reply_markup=markup)
        bot.register_next_step_handler(m, director_markup_analysis)


def director_markup_analysis(message):  # анализ ответа директора на поребность в удалении записи
    if message.text == 'Да':
        choice_record(message)  # преходит к выбору записи для удаления
    else:
        director_entrance(message)  # возращает директора к основной функции для директора


def choice_record(message):  # выбор записи для удаления директором
    m = bot.send_message(chat_id_director,
                         text="Ответьте на сообщение, которое надо удалить.")
    bot.register_next_step_handler(m, del_record)


@bot.message_handler(func=lambda message: True)
def del_record(message):  # удаление записи
    if message.reply_to_message:
        t = str(message.reply_to_message.text).split()
        data = t[2]
        time = t[4]
        item = str(data) + ' ' + str(time)
        notification_secretary(item)
        sql_update_query = """DELETE from records where tm = ? and dt = ?"""
        cursor.execute(sql_update_query, (time, data))
        conn.commit()
        bot.send_message(chat_id_director, text="Удалена.")
    else:
        bot.send_message(chat_id_director, text="Неверное действие.")
    director_entrance(message)


def schedule_checker():
    while True:
        schedule.run_pending()
        sleep(1)


def function_to_run():  # возвращает записи на сегодня
    dt = list()
    day = str(date.today()).split('-')
    day.reverse()
    day = '.'.join(day)
    dt.append(day)
    cursor.execute('SELECT * FROM records WHERE dt = ? ', dt)
    results = cursor.fetchall()
    n = 0
    if not results:  # проверка наличия записей в базе данных
        bot.send_message(chat_id_director,
                         f"Нет записи на {dt[0]}.",
                         parse_mode='html')
    else:
        results.sort(key=sorting)
        for i in results:
            n += 1
            bot.send_message(chat_id_director,
                             str(n) + ') Дата: ' + dt[0] + '\n    Время: ' + str(i[3]) + '\n    Причина: ' + str(i[1]),
                             parse_mode='html')


# ассистент


def assistant_welcome(message):  # приветствие с ассистентом
    bot.send_message(chat_id_assistant,
                     "Успешный вход в систему ассистента!",
                     parse_mode='html')
    assistant_functions(message)


def assistant_functions(message):  # вывод кнопок с функциями ассистентом
    m = bot.send_message(chat_id_assistant,
                         text="Выберите нужную кнопку.",
                         reply_markup=button.assistant_markup())
    bot.register_next_step_handler(m, assistant_function)


def assistant_function(message):  # выбор функции ассистентом
    if message.text == "Ввод актуального":
        write_actual(message)
    elif message.text == "Просмотр и удаление актуального":
        del_actual(message)
    else:
        bot.send_message(message.chat.id,
                         text="Неверное действие.")
        assistant_functions(message)


def write_actual(message):  # ввод текста актуального
    m = bot.send_message(chat_id_assistant,
                         text="Напишите часто задаваемые вам вопросы и ответы на них.",
                         reply_markup=button.del_buttons())
    bot.register_next_step_handler(m, adding_actual)


def adding_actual(message):  # довабдение актуального в базу данных
    text_actual = (None, message.text)
    cursor.execute('INSERT INTO news (id, text_new) VALUES (?, ?)', text_actual)
    conn.commit()
    markup = button.actual_markup()
    m = bot.send_message(chat_id_assistant,
                         text="Выберите нужную кнопку",
                         reply_markup=markup)
    bot.register_next_step_handler(m, next_actual)


def next_actual(message):
    if message.text == "Добавить еще актуальное":
        write_actual(message)  # возвращение к добавлению актуального админа
    elif message.text == "Назад":
        assistant_functions(message)  # возвращение к функциям админа
    else:
        bot.send_message(chat_id_assistant,
                         text="Неверное действие.")
        assistant_functions(message)


def del_actual(message):  # вывод актуального для удаления ассистентом
    bot.send_message(chat_id_assistant,
                     text="Актульное:",
                     reply_markup=button.del_buttons())
    cursor.execute('SELECT text_new FROM news')
    results = cursor.fetchall()
    if not results:  # нет актуального в базе данных
        bot.send_message(chat_id_assistant,
                         text="Пусто в актуальном.")
        assistant_function(message)
    else:  # есть актуальное в базе данных
        for i in results:
            bot.send_message(chat_id_assistant, i, parse_mode='html')
        answer_to_del(message)


def answer_to_del(message):  # выбор актуального для удаления
    m = bot.send_message(chat_id_assistant,
                         text='Ответьте на сообщение, которое надо удалить.'
                              '\nЕсли Вы не хотите удалять актуальное, '
                              '\nнапишите слово "Назад".')
    bot.register_next_step_handler(m, removal_actual)


@bot.message_handler(func=lambda message: True)
def removal_actual(message):  # удаление выбранного актуального
    if message.reply_to_message:  # проверка отвеченное ли это сообщение
        t = str(message.reply_to_message.text)
        cursor.execute('SELECT text_new FROM news')
        results = cursor.fetchall()
        if (t,) in results:  # проверка есть ли в базе данных сообщение, на которое ответили
            sql_update_query = """DELETE from news where text_new = ?"""
            cursor.execute(sql_update_query, (t,))
            conn.commit()
            bot.send_message(chat_id_assistant,
                             text="Удалена.")
            assistant_functions(message)  # возвращает в функции админа
        else:
            m = bot.send_message(chat_id_assistant,
                                 text="Выберите нужную кнопку.",
                                 reply_markup=button.removal_actual_markup())
            bot.register_next_step_handler(m, checking_for_actual)  # вывод кнопок при неверном действии
    elif message.text == "Назад" or message.text == "назад":
        assistant_functions(message)
    else:
        m = bot.send_message(chat_id_assistant,
                             text="Выберите нужную кнопку",
                             reply_markup=button.removal_actual_markup())
        bot.register_next_step_handler(m, checking_for_actual)  # вывод кнопок при неверном действии


def checking_for_actual(message):
    if message.text == "Попробовать ещё раз":
        del_actual(message)  # следующая попытка корректного ответа на сообщение, которое надо удалить
    elif message.text == "Назад":
        assistant_functions(message)  # возращение к функциям ассистентом
    else:
        bot.send_message(message.chat.id,
                         text="Неверное действие.")
        assistant_functions(message)


# обычный пользователь


def functions_user(message):  # функции обычного пользователя
    m = bot.send_message(message.chat.id,
                         text="Выберите нужную кнопку",
                         reply_markup=button.user_markup())  # вывод кнопок с функциями обычного пользователя
    bot.register_next_step_handler(m, user_markup_analysis)


def user_markup_analysis(message):  # выбор определеннной функции обычного пользователя
    if message.text == 'Актуальное':  # переход к выбранной функции
        actual(message)
    elif message.text == 'Справка':
        reference(message)
    else:
        bot.send_message(message.chat.id,
                         text="Неверное действие.")
        functions_user(message)


def actual(message):  # вывод актуального для обычного пользователя
    cursor.execute('SELECT text_new FROM news')
    results = cursor.fetchall()
    if not results:  # проверка наличия актуального в базе данных
        bot.send_message(message.chat.id,
                         text="Пусто в актуальном.")
    else:
        for i in results:  # ввывод актуального
            bot.send_message(message.chat.id, i, parse_mode='html')
    functions_user(message)  # возвращает в функции обычного пользователя


# справка


def reference(message):  # ввод имеми для сбора информации для справки
    dell = telebot.types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id,
                     text="Введите нужную информацию для спраки:",
                     reply_markup=dell)
    m = bot.send_message(message.chat.id,
                         text="ФИО ребенка полностью", )
    bot.register_next_step_handler(m, collecting_reference_name)


def collecting_reference_name(message):  # считивание имеми для сбора информации для справки
    global information_for_reference
    information_for_reference.append(message.text)
    m = bot.send_message(message.chat.id,
                         text="Класс")
    bot.register_next_step_handler(m, collecting_reference_class)


def collecting_reference_class(message):  # ввод даты рождения для сбора информации для справки
    global information_for_reference
    information_for_reference.append(message.text)
    m = bot.send_message(message.chat.id,
                         text="Дата рождения ребенка")
    bot.register_next_step_handler(m, collecting_reference_data)


def collecting_reference_data(message):  # считивание даты рождения для сбора информации для справки
    global information_for_reference
    information_for_reference.append(message.text)
    created_reference(message)


def creating_reference(items):  # формирование справки и ее заполнение
    doc = docx.Document('справка.docx')
    for i in doc.paragraphs:
        tx = str(i.text)
        if "%%%" in i.text:
            tb = str(date.today()).split('-')
            tb.reverse()
            tb = '.'.join(tb)
            tx = tx.replace("%%%", str(tb))
            i.text = tx
        if "===" in i.text:
            tx = tx.replace("===", items[0])
            i.text = tx
        if "+++" in i.text:
            tx = tx.replace("+++", items[2])
            i.text = tx
        if "#" in i.text:
            i.text = tx.replace("#", items[1])
        if "*" in i.text:
            dt = str(date.today()).split('-')
            n = int(dt[0])
            try:
                n += (11 - int(items[1].split()[0]))
                if int(dt[1]) > 8:
                    n += 1
                i.text = tx.replace("*", '31.08.' + str(n))
            except:
                i.text = tx.replace("*", "Невозможен расчет даты выпуска")
    doc.save("новая_справка.docx")


def created_reference(message):  # формирование справки и ее заполнение
    creating_reference(information_for_reference)
    bot.send_message(message.chat.id,
                     'Ваша справка успешна создана!',
                     reply_markup=button.del_buttons())
    functions_user(message)
    forward_dock()


def convert_to_binary_data():  # открытие справки
    with open('новая_справка.docx', 'rb') as file:
        blob_data = file.read()
    return blob_data


def forward_dock():  # внесение спарвку в базу данных
    sqlite_insert_blob_query = """INSERT INTO docs (id, doc) VALUES (?, ?)"""
    resume = convert_to_binary_data()
    data_tuple = (None, resume)
    cursor.execute(sqlite_insert_blob_query, data_tuple)
    conn.commit()


# секретарь


def secretary_welcome(message):  # приветствие с секретарем
    bot.send_message(message.chat.id,
                     "Успешный вход в систему секретаря!",
                     parse_mode='html')
    functions_secretary(message)


def functions_secretary(message):  # функции секретаря
    m = bot.send_message(message.chat.id,
                         text="Выберите нужную кнопку",
                         reply_markup=button.secretary_markup())  # вызов кнопок с функциями секретаря
    bot.register_next_step_handler(m, function_secretary)


def function_secretary(message):  # выбор определенной функции секретаря
    if message.text == "Проверка справок":
        check_doc(message)
    elif message.text == "Ввод записи":
        adding_time_for_record(message)
    elif message.text == "Проверка и удаление записи":
        check_secretary_record(message)
    else:
        bot.send_message(message.chat.id,
                         text="Неверное действие.")
        functions_secretary(message)


def check_secretary_record(message):  # выбор дня для просмотра записи к директору
    bot.send_message(message.chat.id,
                     "\nНа какой день Вы хотите посмотреть записи?",
                     parse_mode='html')
    checking_secretary_record(message)


def checking_secretary_record(message):  # получение дня от директора, на который он хочет посмотреть записи
    m = bot.send_message(message.chat.id,
                         text="Корректный ответ:\n22.01.2022")
    bot.register_next_step_handler(m, date_of_recording_analysis_secretary)


def date_of_recording_analysis_secretary(message):  # вывод записей на выбранный директором день
    data = list()
    data.append(message.text)
    cursor.execute('SELECT * FROM records WHERE dt = ? ', data)
    results = cursor.fetchall()
    if not results:  # нет записей
        bot.send_message(message.chat.id,
                         "Нет записи на этот день.",
                         parse_mode='html')
        functions_secretary(message)
    else:  # есть записи
        results.sort(key=sorting)
        n = 0
        for i in results:  # вывод записей на выбранный день
            n += 1
            bot.send_message(message.chat.id,
                             str(n) + ') Дата: ' + str(data[0]) + '\n    Время: ' + str(i[3]) + '\n    Причина: ' + str(
                                 i[1]),
                             parse_mode='html')
        markup = button.data_analysis_markup()  # узнаем нужно ли удалить запись
        m = bot.send_message(message.chat.id,
                             text="Хотите отменить запись?",
                             reply_markup=markup)
        bot.register_next_step_handler(m, secretary_markup_analysis)


def secretary_markup_analysis(message):  # анализ ответа директора на поребность в удалении записи
    if message.text == 'Да':
        choice_record_secretary(message)  # преходит к выбору записи для удаления
    elif message.text == 'Нет':
        functions_secretary(message)  # возращает директора к основной функции для директора
    else:
        bot.send_message(message.chat.id, text="Неверное действие.")
        functions_secretary(message)


def choice_record_secretary(message):  # выбор записи для удаления
    m = bot.send_message(message.chat.id,
                         text="Ответьте на сообщение, "
                              "\nкоторое надо удалить.")
    bot.register_next_step_handler(m, del_record_secretary)


@bot.message_handler(func=lambda message: True)
def del_record_secretary(message):  # удаление записи
    if message.reply_to_message:  # если ответ на сообщение
        t = str(message.reply_to_message.text).split()
        time = t[4]
        data = t[2]
        sql_update_query = """DELETE from records where tm = ? and dt = ?"""
        cursor.execute(sql_update_query, (time, data))
        conn.commit()
        bot.send_message(message.chat.id, text="Удалена.")
    else:
        bot.send_message(message.chat.id, text="Неверное действие.")
    functions_secretary(message)


def write_to_file(data, filename, num):  # чтение справки
    with open(filename, 'wb') as file:  # открытие справки
        file.write(data)
    bot.send_document(chat_id=chat_id_secretary, document=open(f"справка_{str(num)}.docx", 'rb'))  # вывод справки


def del_doc(message):  # удаление справки по номеру
    if message.text == "стоп" or message.text == "Стоп":  # остановление удаления справки
        functions_secretary(message)
    else:
        try:  # удаление из базы данных справки
            num = int(message.text)
            sql_update_query = """DELETE from docs where id = ?"""
            cursor.execute(sql_update_query, (num,))
            conn.commit()
        except:  # при ошибки
            bot.send_message(message.chat.id, text='Неверный ввод номера справки.'
                                                   '\nПопробуйте ещё раз или напишите слово "Стоп".')
        num_doc_to_del(message)


def check_doc(message):  # чтение справок из базы данных
    sql_fetch_blob_query = """SELECT * from docs"""
    cursor.execute(sql_fetch_blob_query)
    record = cursor.fetchall()
    for i in record:
        resume_file = i[1]
        resume_path = os.path.join(f"справка{str(i[0])}.docx")
        write_to_file(resume_file, resume_path, i[0])
    num_doc_to_del(message)


def num_doc_to_del(message):  # ввод номера справки для удаления
    m = bot.send_message(message.chat.id,
                         text="Введите номер справки."
                              '\nЕсли Вы хотите перестать удалять справки,'
                              '\nто напишите слово "Стоп".')
    bot.register_next_step_handler(m, del_doc)


def notification_secretary(t):  # уведомление о удалении директором записи
    bot.send_message(chat_id_secretary,
                     "Директор удалил запись: " + '\n' + t,
                     parse_mode='html')


def adding_time_for_record(message):  # получение информации о актуальном от секретаря
    m = bot.send_message(message.chat.id,
                         text="Напишите дату и время, когда возможна запись к директору."
                              "\nПример:"
                              "\n12.12.2022 18:00-19:00")
    bot.register_next_step_handler(m, record_analysis)


def record_analysis(message):  # проверка корректрости информации для записи к директору
    data_time = message.text.split()
    if len(data_time) == 2:
        if len(data_time[0]) == 10 and len(data_time[1]) == 11:
            data = data_time[0].split('.')
            time = data_time[1].split('-')
            if len(data) == 3 and len(time) == 2:
                time_start = time[0].split(':')
                time_end = time[1].split(':')
                if len(time_end) == 2 and len(time_start) == 2:
                    try:
                        if (int(data[0]) <= 31 and int(data[1]) <= 12 and int(data[2])
                                and int(time_start[0]) <= 23 and int(time_end[0]) <= 23
                                and int(time_start[1]) <= 59 and int(time_end[1]) <= 59):
                            information_for_record.append('.'.join(data))
                            information_for_record.append('-'.join(time))
                            write_reason_for_record(message)
                        else:
                            m = bot.send_message(message.chat.id,
                                                 text="Выберите нужную кнопку",
                                                 reply_markup=button.adding_time_for_records_markup())
                            bot.register_next_step_handler(m, function_secretary)
                    except:
                        m = bot.send_message(message.chat.id,
                                             text="Выберите нужную кнопку",
                                             reply_markup=button.adding_time_for_records_markup())
                        bot.register_next_step_handler(m, function_secretary)
                else:
                    m = bot.send_message(message.chat.id,
                                         text="Выберите нужную кнопку",
                                         reply_markup=button.adding_time_for_records_markup())
                    bot.register_next_step_handler(m, function_secretary)
            else:
                m = bot.send_message(message.chat.id,
                                     text="Выберите нужную кнопку",
                                     reply_markup=button.adding_time_for_records_markup())
                bot.register_next_step_handler(m, function_secretary)
        else:
            m = bot.send_message(message.chat.id,
                                 text="Выберите нужную кнопку",
                                 reply_markup=button.adding_time_for_records_markup())
            bot.register_next_step_handler(m, function_secretary)
    else:
        m = bot.send_message(message.chat.id,
                             text="Выберите нужную кнопку",
                             reply_markup=button.adding_time_for_records_markup())
        bot.register_next_step_handler(m, function_secretary)


def wrong_for_reference(message):  # при некорректном вводе информации для записи к директору
    global information_for_record
    information_for_record.clear()
    if message.text == 'Попробовать ещё раз':
        adding_time_for_record(message)  # возвращает началу ввода информации для записи к директору
    elif message.text == 'Назад':
        functions_secretary(message)  # возвращает к функциям обычного пользователя
    else:
        bot.send_message(message.chat.id,
                         text="Неверное действие.")
        functions_secretary(message)


def write_reason_for_record(message):  # получение причины записи к директору
    m = bot.send_message(message.chat.id,
                         text="Напишите причину записи к директору.")
    bot.register_next_step_handler(m, read_reason_for_record)


def read_reason_for_record(message):  # довавление секретарем записи к директору в базу данных
    global information_for_record
    information_for_record.append(message.text)
    ans = write_record(information_for_record)  # внесение записи в базу данных и проверка на пустоту ячейки для записи
    information_for_record.clear()
    bot.send_message(message.chat.id,
                     ans,
                     parse_mode='html')
    functions_secretary(message)  # возвращает в функции секретаря


def write_record(items):  # внесение записи в базу данных и проверка на пустоту
    inf = (items[0], items[1])
    cursor.execute('SELECT * FROM records WHERE dt = ? AND tm = ?', inf)
    results = cursor.fetchall()
    if not results:  # внесение записи в базу данных
        record = list()
        record.append(None)
        record.append(items[2])
        record.append(items[0])
        record.append(items[1])
        cursor.execute('INSERT INTO records (id, rs, dt, tm) VALUES (?, ?, ?, ?)', record)
        conn.commit()
        return "Успешно добавленна запись!"  # вывод вердикта
    else:  # уже есть запись на это время и день
        return "На это время и день уже существует запись."  # вывод вердикта


def sorting(items):  # сортировка по времени
    return items[3]


if __name__ == '__main__':
    schedule.every().day.at("7:00").do(function_to_run)  # вызов функции ежедневного напоминания директору о записи
    Thread(target=schedule_checker).start()
    bot.polling(none_stop=True, interval=0)
