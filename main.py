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
                         text="Корректный ответ:"
                              "\n00.00.0000")
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
                             '№' + str(n) + '\nДата: ' + data[0] + '\nВремя: ' + str(i[2]) + '\nПричина: ' + str(
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
                             '№' + str(n) + '\nДата: ' + dt[0] + '\nВремя: ' + str(i[3]) + '\nПричина: ' + str(i[1]),
                             parse_mode='html')


def del_record(message, data):  # удаление записи
    time = message.text
    cursor.execute('SELECT * FROM records WHERE dt = ? and tm = ? ', (data, time))
    res = cursor.fetchall()
    sql_update_query = """DELETE from records where tm = ? and dt = ?"""
    cursor.execute(sql_update_query, (time, data))
    conn.commit()
    bot.send_message(message.chat.id, "Запись успешно удалена.", parse_mode='html')
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
    bot.register_next_step_handler(m, as_adding_actual)


def as_adding_actual(message):  # довабдение актуального в базу данных
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
        my_record(message)
    else:
        functions_user(message)


def dell_record_user_1(message):
    m = bot.send_message(message.chat.id,
                     "Какую запись хотите удалить?"
                     "\nКорректный ответ:"
                     "\n00.00.0000 00:00-00:00",
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
    functions_user(message)  # возвращает в функции обычного пользователя



def my_record(message): # просмотр записей пользователя
    id_us = list()
    id_us.append(message.chat.id)
    cursor.execute('SELECT * FROM records WHERE user = ? ', id_us)
    results = cursor.fetchall()
    if not results:
        bot.send_message(message.chat.id,
                         text="Пусто.")
    else:
        n = 0
        for i in results:
            n += 1
            bot.send_message(message.chat.id,
                             '№' + str(n) + '\nДата: ' + str(i[1]) + '\nВремя: ' + str(i[2]), parse_mode='html')
    functions_user(message)  # возвращает в функции обычного пользователя



def time_user_write_1(message):  # получение дня от пользователя, на которую пользователей хочет записаться
    m = bot.send_message(message.chat.id,
                         text="На какой день вы хотите записаться?"
                              "\nКорректный ответ:"
                              "\n00.00.0000")
    bot.register_next_step_handler(m, time_user_write_2)


def time_user_write_2(message):  # обработка дня от пользователя, на которую пользователей хочет записаться
    data = list()
    data.append(message.text)
    cursor.execute('SELECT * FROM records where dt = ? and user is NULL', data)
    results = cursor.fetchall()
    if not results:  # проверка наличия времени
        bot.send_message(message.chat.id,
                         text="На выбранный день нет слотов.")
        functions_user(message)
    else:
        times = []
        for i in results:  # ввывод времени
            bot.send_message(message.chat.id, str(i[2]), parse_mode='html')
            times.append(i[2])
        m = bot.send_message(message.chat.id,
                             text="Выберите время или нажмите кнопку Назад, если вам не подходят данные слоты."
                                  "\nКорректный ответ:"
                                  "\n00:00-00:00", reply_markup=button.removal_records_markup())
        bot.register_next_step_handler(m, time_user_write_3, message.text, times)


def time_user_write_3(message, data, times): # ввод причины для записи
    if message.text == 'Назад' or message.text == 'назад':
        functions_user(message)
    elif message.text not in times:
        bot.send_message(message.chat.id,
                         text="Неверный ввод.",  reply_markup=button.del_buttons())
        functions_user(message)
    else:
        time = message.text
        time = map(int, time.split())
        m = bot.send_message(message.chat.id,
                             text="Напишите свое полное имя, должность и причину записи.",
                             reply_markup=button.del_buttons())
        bot.register_next_step_handler(m, time_user_write_4, data, time)


def time_user_write_4(message, data, time): # внесение данных о записи
    bot.send_message(message.chat.id,
                         message.text)
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
