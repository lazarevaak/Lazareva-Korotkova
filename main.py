#!/usr/bin/env python
# _*_ coding: utf-8 _*_

import schedule
import telebot

import docx
import os

import database
import button
import tokens
import id

from datetime import date
from time import sleep
from threading import Thread

# токен чат-бота

bot = telebot.TeleBot(tokens.token_bot())

# id пользователей, кроме обычных пользователей

chat_id_director = id.director()
chat_id_secretary = id.secretary()
chat_id_assistant = id.assistant()

# сбор информации

information_for_reference = []
information_for_record = []

# создание и подключение базы данных

conn = database.connects()
cursor = database.cursors(conn)
database.executes(cursor)

# начало работы чат-бота


@bot.message_handler(commands=['start'])
def welcome(message):  # команда /start
    m = bot.send_message(message.chat.id,
                         "Добро пожаловать!"
                         "\nВас приветствует чат-бот секретаря школы 444."
                         "\nПредставьтесь, пожалуйста!",
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
        id = [i[0] for i in results]
        if len(results) == 0 or user_id not in id:  # проверка наличия пользователя в базе данных
            cursor.execute('INSERT INTO users (us_id, us_name) VALUES (?, ?)', user)
            conn.commit()
        welcome_user(message)


# директор


def director_welcome(message):  # приветствие с директором
    bot.send_message(chat_id_director,
                     "Успешный вход в систему директора!",
                     parse_mode='html')
    director_entrance(message)


def director_entrance(message):  # выбор дня для просмотра записи к директору
    bot.send_message(chat_id_director,
                     "Директор, на какой день Вы хотите посмотреть записи?",
                     parse_mode='html')
    director_function(message)


def director_function(message):  # получение дня от директора, на который он хочет посмотреть записи
    m = bot.send_message(chat_id_director,
                         text="Корректный ответ:\n20.02.2000")
    bot.register_next_step_handler(m, date_of_recording_analysis)


def date_of_recording_analysis(message):  # вывод записей на выбранный директором день
    data = list()
    data.append(message.text)
    cursor.execute('SELECT * FROM records WHERE dt = ? ', data)
    results = cursor.fetchall()
    if not results:  # нет записей
        bot.send_message(chat_id_director,
                         "Нет записи на этот день",
                         parse_mode='html')
        director_entrance(message)
    else:  # есть записи
        results.sort(key=sorting)
        n = 0
        for i in results:  # вывод записей на выбранный день
            n += 1
            bot.send_message(chat_id_director,
                             str(n) + ') Дата: ' + data[0] + '\n    Время: ' + str(i[2]) + '\n    Причина: ' + str(
                                 i[0])  + '\n    Записавшийся: ' + str(i[3]),
                             parse_mode='html')
        markup = button.data_analysis_markup()  # узнаем нужно ли удалить запись
        m = bot.send_message(chat_id_director,
                             text="Хотите отменить запись?",
                             reply_markup=markup)
        bot.register_next_step_handler(m, director_markup_analysis, data)



def director_markup_analysis(message, data):# анализ ответа директора на поребность в удалении записи
    if message.text == 'Нет':
        director_entrance(message)
    elif message.text == 'Да':
        data = data[0]
        choice_record_dir(message, data)  # преходит к выбору записи для удаления


def choice_record_dir(message, data):  # выбор записи для удаления директором
    m = bot.send_message(message.chat.id,
                         text="Напишите время записи, на которое вы хотите удалить запись.",
                         reply_markup=button.del_buttons())
    bot.register_next_step_handler(m, del_record, data)


def choice_record_sec(message, data):  # выбор записи для удаления директором
    m = bot.send_message(message.chat.id,
                         text="Напишите время записи, на которое вы хотите удалить запись.",
                         reply_markup=button.del_buttons())
    bot.register_next_step_handler(m, del_record, data)


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


def del_record(message, data):  # удаление записи
    time = message.text
    cursor.execute('SELECT * FROM records WHERE dt = ? and tm = ? ', (data, time))
    res = cursor.fetchall()
    sql_update_query = """DELETE from records where tm = ? and dt = ?"""
    cursor.execute(sql_update_query, (time, data))
    conn.commit()
    if message.chat.id == chat_id_director:
        director_entrance(message)
    elif message.chat.id == chat_id_secretary:
        functions_secretary(message)


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
        assistant_functions(message)


def del_actual(message):  # вывод актуального для удаления ассистентом
    bot.send_message(chat_id_assistant,
                     text="Актуальное:",
                     reply_markup=button.del_buttons())
    cursor.execute('SELECT text_new FROM news')
    results = cursor.fetchall()
    if not results:  # нет актуального в базе данных
        bot.send_message(chat_id_assistant,
                         text="Пусто в актуальном.")
        assistant_functions(message)
    else:  # есть актуальное в базе данных
        for i in results:
            bot.send_message(chat_id_assistant, i, parse_mode='html')
        answer_to_del(message)


def answer_to_del(message):  # выбор актуального для удаления
    m = bot.send_message(message.chat.id,
                         text='Ответьте на сообщение, которое надо удалить.'
                              '\nЕсли не хотите удалять актуальное, напишите слово "Назад".')
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
        assistant_functions(message)


# обычный пользователь


def welcome_user(message): # приветствие с обычным пользователем по имени из базы данных
    name = list()
    name.append(message.chat.id)
    cursor.execute('SELECT us_name FROM users WHERE us_id = ? ', name)
    results = cursor.fetchall()
    bot.send_message(message.chat.id,
                     text=str(results[0][0]) + ","
                                               "\nдобро пожаловать!")
    functions_user(message)


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
    elif message.text == 'Запись':
        reсord_user_all_1(message)
    else:
        functions_user(message)


def reсord_user_all_1(message):  # функции обычного пользователя
    m = bot.send_message(message.chat.id,
                         text="Выберите нужную кнопку",
                         reply_markup=button.record_user_markup())  # вывод кнопок с функциями обычного пользователя
    bot.register_next_step_handler(m, reсord_user_all_2)


def reсord_user_all_2(message):
    if message.text == 'Записаться':
        time_user_write_1(message)
    elif message.text == 'Удалить':
        dell_record_user_1(message)
    elif message.text == 'Мои записи':
        print(0)
        my_record(message)
    else:
        functions_user(message)


def dell_record_user_1(message):
    m = bot.send_message(message.chat.id,
                     "Какую запись хотите удалить?"
                     "\nКорректный ответ:"
                     "\n20.02.2020 18:00-19:00",
                     parse_mode='html', reply_markup=button.del_buttons())
    bot.register_next_step_handler(m, dell_record_user_2)


def dell_record_user_2(message):
    try:
        data, time = message.text.split()
        sql_update_query = """DELETE from records where tm = ? and dt = ?"""
        cursor.execute(sql_update_query, (time, data))
        conn.commit()
        bot.send_message(message.chat.id,
                         text="Удаление прошло успешно.")
    except:
        bot.send_message(message.chat.id,
                         text="Неверный ввод.")
    functions_user(message)



def my_record(message):  # удаление справки по номеру
    id_us = list()
    id_us.append(message.chat.id)
    cursor.execute('SELECT * FROM records WHERE user = ? ', id_us)
    results = cursor.fetchall()
    if not results:  # проверка наличия актуального в базе данных
        bot.send_message(message.chat.id,
                         text="Пусто.")
    else:
        n = 0
        for i in results:  # вывод записей на выбранный день
            n += 1
            bot.send_message(message.chat.id,
                             str(n) + ') Дата: ' + str(i[1]) + '\n    Время: ' + str(i[2]), parse_mode='html')
    functions_user(message)  # возвращает в функции обычного пользователя



def time_user_write_1(message):  # получение дня от директора, на который он хочет посмотреть записи
    m = bot.send_message(message.chat.id,
                         text="На какой день Вы хотите записаться?"
                              "\nКорректный ответ:"
                              "\n20.02.2000")
    bot.register_next_step_handler(m, time_user_write_2)


def time_user_write_2(message):
    print(message.text)# вывод актуального для обычного пользователя
    data = list()
    data.append(message.text)
    cursor.execute('SELECT * FROM records where dt = ?', data)
    results = cursor.fetchall()
    if not results:  # проверка наличия актуального в базе данных
        bot.send_message(message.chat.id,
                         text="На выбранный день нет слотов.")
        functions_user(message)
    else:
        for i in results:  # ввывод актуального
            bot.send_message(message.chat.id, str(i[2]), parse_mode='html')
        m = bot.send_message(message.chat.id,
                             text="Выберите время из предложенных."
                                  "\nКорректный ответ:"
                                  "\n20.02.2000")
        bot.register_next_step_handler(m, time_user_write_3, message.text)
      # возвращает в функции обычного пользователя


def time_user_write_3(message, data):
    time = message.text
    m = bot.send_message(message.chat.id,
                         text="Напишите свое полное имя, должность и причину записи.")
    bot.register_next_step_handler(m, time_user_write_4, data, time)


def time_user_write_4(message, data, time):
    sql_update_query = """DELETE from records where tm = ? and dt = ?"""
    cursor.execute(sql_update_query, (time, data))
    conn.commit()
    sqlite_insert_blob_query = """INSERT INTO records (rs, dt, tm, user) VALUES (?, ?, ?, ?)"""
    data_tuple = (message.text, data, time, message.chat.id)
    cursor.execute(sqlite_insert_blob_query, data_tuple)
    conn.commit()
    bot.send_message(message.chat.id,
                         text="Регистрация прошла успешно.")
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
                         text="ФИО ребенка полностью")
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
    bot.send_message(chat_id_secretary,
                     "Успешный вход в систему секретаря!",
                     parse_mode='html')
    functions_secretary(message)


def functions_secretary(message):  # функции секретаря
    m = bot.send_message(chat_id_secretary,
                         text="Выберите нужную кнопку",
                         reply_markup=button.secretary_markup())  # вызов кнопок с функциями секретаря
    bot.register_next_step_handler(m, function_secretary)


def function_secretary(message):  # выбор определенной функции секретаря
    if message.text == "Проверка справок":
        check_doc(message)
    elif message.text == "Ввод записи":
        adding_time_for_record(message)
    elif message.text == "Удаление и просмотр записи":
        del_function_rec(message)
    else:
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
            bot.send_message(chat_id_secretary, text='Удалена.')
        except:  # при ошибки
            bot.send_message(chat_id_secretary, text='Неверный ввод номера справки.'
                                                   '\nПопробуйте ещё раз или напишите слово "Стоп".',
                             reply_markup=button.del_buttons())
        num_doc_to_del(message)


def check_doc(message):  # чтение справок из базы данных
    sql_fetch_blob_query = """SELECT * from docs"""
    cursor.execute(sql_fetch_blob_query)
    record = cursor.fetchall()
    if len(record) == 0:
        bot.send_message(chat_id_secretary, text='Нет справок.', reply_markup=button.del_buttons())
        functions_secretary(message)
    else:
        for i in record:
            resume_file = i[1]
            resume_path = os.path.join(f"справка_{str(i[0])}.docx")
            write_to_file(resume_file, resume_path, i[0])
        num_doc_to_del(message)


def num_doc_to_del(message):  # ввод номера справки для удаления
    m = bot.send_message(chat_id_secretary,
                         text="Введите номер справки."
                              '\nЕсли хотите перестать удалять справки, то напишите слово "Стоп".',
                         reply_markup=button.del_buttons())
    bot.register_next_step_handler(m, del_doc)


def notification_secretary(t, id_user):  # уведомление о удалении директором записи
    bot.send_message(chat_id_secretary,
                     "Запись удалена: " + '\n' + t,
                     parse_mode='html')
    bot.send_message(chat_id_director,
                     "Запись удалена: " + '\n' + t,
                     parse_mode='html')
    bot.send_message(id_user,
                     "Запись удалена: " + '\n' + t,
                     parse_mode='html')


def adding_time_for_record(message):  # получение информации о актуальном от секретаря
    m = bot.send_message(chat_id_secretary,
                         text="Напишите дату и время, когда возможна запись к директору."
                              "\nПример:"
                              "\n12.12.2022 18:00-19:00", reply_markup=button.del_buttons())
    bot.register_next_step_handler(m, record_add_time_day)


def record_add_time_day(message):
    n = message.text.split()
    if len(n) == 2:
        data = n[0].split('.')
        time = n[1].split('-')
        if len(data) == 3 and len(time) == 2:
            start = time[0].split(':')
            stop = time[1].split(':')
            if len(start) == 2 and len(stop) == 2:
                try:
                    a = map(int, data)
                    b = map(int, start)
                    c = map(int, stop)
                    cursor.execute('SELECT * FROM records WHERE dt = ?  and tm = ?', (n[0], n[1]))
                    results = cursor.fetchall()
                    if not results:  # проверка наличия записей в базе данных
                        sqlite_insert_blob_query = """INSERT INTO records (rs, dt, tm, user) VALUES (?, ?, ?, ?)"""
                        data_tuple = (None, n[0], n[1], None)
                        cursor.execute(sqlite_insert_blob_query, data_tuple)
                        conn.commit()
                        bot.send_message(chat_id_secretary,
                                             text="Успешно добавлено.")
                    else:
                        bot.send_message(chat_id_secretary,
                                         text="Уже создан даннный слот.")
                except:
                    bot.send_message(chat_id_secretary,
                                     text="Ошибка ввода.")
            else:
                bot.send_message(chat_id_secretary,
                                 text="Ошибка ввода.")
        else:
            bot.send_message(chat_id_secretary,
                             text="Ошибка ввода.")
    else:
        bot.send_message(chat_id_secretary,
                         text="Ошибка ввода.")
    functions_secretary(message)


def del_function_rec(message):  # получение дня от директора, на который он хочет посмотреть записи
    m = bot.send_message(message.chat.id,
                         text="На какой день Вы хотите посмотреть записи?"
                              "\nКорректный ответ:"
                              "\n20.02.2000", reply_markup=button.del_buttons())
    bot.register_next_step_handler(m, sec_date_of_recording_analysis)


def sec_date_of_recording_analysis(message):  # вывод записей на выбранный директором день
    data = list()
    day = message.text
    data.append(message.text)
    cursor.execute('SELECT * FROM records WHERE dt = ? ', data)
    results = cursor.fetchall()
    if not results:  # нет записей
        bot.send_message(message.chat.id,
                         "Нет записи на этот день",
                         parse_mode='html')
        if message.chat.id == id.director():
            director_entrance(message)
        elif message.chat.id == id.secretary():
            functions_secretary(message)
        else:
            functions_user(message)
    else:  # есть записи
        results.sort(key=sorting)
        n = 0
        for i in results:  # вывод записей на выбранный день
            n += 1
            bot.send_message(message.chat.id,
                             str(n) + ') Дата: ' + data[0] + '\n    Время: ' + str(i[2]) + '\n    Причина: ' + str(i[0])
                             + '\n    Записавшийся: ' + str(i[3]),
                             parse_mode='html')
        markup = button.data_analysis_markup()  # узнаем нужно ли удалить запись
        m = bot.send_message(message.chat.id,
                             text="Хотите отменить запись?",
                             reply_markup=markup)
        bot.register_next_step_handler(m, sec_markup_analysis, day)



def sec_markup_analysis(message, day):
    # анализ ответа директора на поребность в удалении записи
    if message.text == 'Нет':
        functions_secretary(message)
    elif message.text == 'Да':
        choice_record_sec(message, day)  # преходит к выбору записи для удаления


def sorting(items):  # сортировка по времени
    return items[3]


if __name__ == '__main__':
    schedule.every().day.at("07:00").do(function_to_run)  # вызов функции ежедневного напоминания директору о записи
    Thread(target=schedule_checker).start()
    bot.polling(none_stop=True, interval=0)
