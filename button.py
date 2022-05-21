from telebot import types
import telebot

def record_user_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    bt1 = types.KeyboardButton("Записаться")
    bt2 = types.KeyboardButton("Удалить")
    bt3 = types.KeyboardButton("Мои записи")
    markup.add(bt1, bt2, bt3)
    return markup


def user_markup(): # функции обычного пользователя
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    bt1 = types.KeyboardButton("Справка")
    bt2 = types.KeyboardButton("Актуальное")
    bt3 = types.KeyboardButton("Запись")
    markup.add(bt1, bt2, bt3)
    return markup


def user_record_markup(): # функции обычного пользователя
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    bt1 = types.KeyboardButton("Записаться на приём")
    bt2 = types.KeyboardButton("Удалить запись")
    markup.add(bt1, bt2)
    return markup


def data_analysis_markup(): # кнопки, чтобы узнать постребность в удаленнии записи
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    bt1 = types.KeyboardButton("Да")
    bt2 = types.KeyboardButton("Нет")
    markup.add(bt1, bt2)
    return markup


def secretary_markup(): # функции секретаря
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    bt1 = types.KeyboardButton("Проверка справок")
    bt2 = types.KeyboardButton("Ввод записи")
    bt3 = types.KeyboardButton("Удаление и просмотр записи")
    markup.add(bt1, bt2, bt3)
    return markup


def actual_markup(): # кнопки с выбором, относящиеся к актуальному
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    bt1 = types.KeyboardButton("Добавить еще актуальное")
    bt2 = types.KeyboardButton("Назад")
    markup.add(bt1, bt2)
    return markup


def adding_time_for_records_markup():  # кнопки, появляющиеся при неправильном вводе даты в записи
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    bt1 = types.KeyboardButton("Попробовать ещё раз")
    bt2 = types.KeyboardButton("Назад")
    markup.add(bt1, bt2)
    return markup


def removal_actual_markup(): # кнопки, появляющиеся при неправильном ответе на сообщение для удаления актуального
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    bt1 = types.KeyboardButton("Попробовать ещё раз")
    bt2 = types.KeyboardButton("Назад")
    markup.add(bt1, bt2)
    return markup


def assistant_markup(): # функции ассистента
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    bt1 = types.KeyboardButton("Ввод актуального")
    bt2 = types.KeyboardButton("Просмотр и удаление актуального")
    markup.add(bt1, bt2)
    return markup


def del_buttons():  # удаление кнопок у пользователей на экране
    dell = telebot.types.ReplyKeyboardRemove()
    return dell