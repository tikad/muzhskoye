# -*- coding: utf-8 -*-

import config
import telebot
from telebot import types
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

bot = telebot.TeleBot(config.token)
Base = declarative_base()


class Adverts(Base):
    __tablename__ = 'adverts'
    id = Column(Integer, primary_key=True)
    text = Column(String)
    category = Column(String)
    size = Column(String)
    price = Column(Integer)
    comments = Column(String)
    chat_id = Column(Integer)
    message_id = Column(String)
    currency = Column(String)
    username = Column(String)

    def __init__(self, text, category, size, currency, price, comments, chat_id, message_id, username):
        self.text = text
        self.category = category
        self.size = size
        self.price = price
        self.comments = comments
        self.chat_id = chat_id
        self.message_id = message_id
        self.currency = currency
        self.username = username


NewAdvert = Adverts(0, 0, 0, 0, 0, 0, 0, 0,0)


@bot.message_handler(commands=['start'])
def start(m):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*[types.KeyboardButton(i) for i in ['Да', 'Нет']])
    msg1 = bot.send_message(m.chat.id, 'Привет, я так понял, что ты хочешь создать объявление, давай начнем. Готов?',
                          reply_markup=keyboard)
    bot.register_next_step_handler(msg1, name)


def name(m):
    if m.text == "Да":
        msg = bot.send_message(m.chat.id, 'Напиши название объявления: укажи бренд и вид вещи')
        bot.register_next_step_handler(msg, size)
    elif m.text == "Нет":
        bot.send_message(m.chat.id, ':(')
    else:
        msg = bot.send_message(m.chat.id, 'Да или нет?')
        bot.register_next_step_handler(msg, name)


def size(message):
    keyboard2 = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard2.add(*[types.KeyboardButton(i) for i in ['Одежда', 'Обувь', 'Аксессуары']])
    msg2 = bot.send_message(message.chat.id, 'Выбери категорию',
                            reply_markup=keyboard2)
    bot.register_next_step_handler(msg2, name2)
    NewAdvert.text = message.text


def name2(m):
    if m.text == "Одежда":
        keyboard3 = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        keyboard3.add(*[types.KeyboardButton(i) for i in ['XXS','XS','S','M','L','XL','XXL']])
        msg = bot.send_message(m.chat.id, 'Время указать размер', reply_markup=keyboard3)
        bot.register_next_step_handler(msg, price)
    elif m.text == "Обувь":
        keyboard3 = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        keyboard3.add(*[types.KeyboardButton(i) for i in ['35','36','37','38','39','40','41', '42','43', '44','45', '46']])
        msg = bot.send_message(m.chat.id, 'Время указать размер', reply_markup=keyboard3)
        bot.register_next_step_handler(msg, price)
    elif m.text == "Аксессуары":
        keyboard4 = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        keyboard4.add(*[types.KeyboardButton(i) for i in ['Доллары', 'Евро', 'Рубли']])
        msg = bot.send_message(m.chat.id, 'Настало время цены. Выбери валюту', reply_markup=keyboard4)
        bot.register_next_step_handler(msg, amount)
    else:
        msg = bot.send_message(m.chat.id, 'Одежда, обувь или аксессуары?')
        bot.register_next_step_handler(msg, name2)
    NewAdvert.category = m.text


def price(message):
    keyboard4 = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard4.add(*[types.KeyboardButton(i) for i in ['Доллары', 'Евро', 'Рубли']])
    msg = bot.send_message(message.chat.id, 'Настало время цены. Выбери валюту', reply_markup=keyboard4)
    bot.register_next_step_handler(msg, amount)
    NewAdvert.size = message.text


def amount(message):
    msg = bot.send_message(message.chat.id, "Введи сумму")
    bot.register_next_step_handler(msg, photo)
    NewAdvert.currency = message.text


def photo(message):
    try:
        int(message.text)
        msg = bot.send_message(message.chat.id, "Пришли фото товара")
        bot.register_next_step_handler(msg, comment)
        NewAdvert.price = message.text
    except ValueError:
        msg = bot.send_message(message.chat.id, "Кажется, сумма указана неверно. Введи число")
        bot.register_next_step_handler(msg, photo)


def comment(message):
    try:
        NewAdvert.message_id = message.photo[len(message.photo) - 1].file_id
        msg = bot.send_message(message.chat.id, "Теперь можешь добавить дополнительную информацию к товару")
        bot.register_next_step_handler(msg, end)
    except:
        msg = bot.send_message(message.chat.id, "Пожалуйста, пришли фото")
        bot.register_next_step_handler(msg, comment)


def end(message):
    NewAdvert.comments = message.text
    NewAdvert.username = message.from_user.username
    bot.send_message(message.chat.id, "Спасибо! Твое объявление было создано! Если хочешь создать ещё одно, нажми /start")
    text = NewAdvert.text + '\n' + NewAdvert.category + '\n' + NewAdvert.currency + ': ' + NewAdvert.price + '\n' + NewAdvert.comments + '\n@' + NewAdvert.username
    bot.send_message(config.chat, text, parse_mode="HTML", disable_web_page_preview=False)
    bot.send_photo(config.chat, photo=NewAdvert.message_id)
bot.polling()
