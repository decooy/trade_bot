import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import os
import dbo as db_

API_TOKEN = os.getenv('token')

bot = telebot.TeleBot(API_TOKEN)
db = db_.database()

user_dict = {}


class User:
    def __init__(self, id):
        self.id = id
        self.deposit = 0
        self.risk = 0


def main_keyboard(id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton('Риск'), KeyboardButton('Депозит'))
    if db.get_sub(id):
        markup.add(KeyboardButton('Отписаться'))
    else:
        markup.add(KeyboardButton('Подписаться'))
    return markup


@bot.message_handler(commands=['start'])
def send_welcome(message):
    id = message.chat.id
    user = db.check_user(id)
    if len(user) == 0:
        bot.send_message(id, '''
BS BOT на связи!
        
Я буду твоим верным помощником в торговле.
        
Но для начала, укажи свой депозит и риск для сделок!
        ''')
        msg = bot.send_message(id, 'Укажи размер депозита в USDT:')
        bot.register_next_step_handler(msg, process_deposit)
    else:
        bot.send_message(id, 'Меню: ', reply_markup=main_keyboard(id))


def process_deposit(message):
    chat_id = message.chat.id
    deposit = message.text
    if str(deposit).isnumeric():
        if int(deposit) < 100:
            msg = bot.send_message(chat_id, 'Депозит не может быть меньше 100 USDT\nУкажи размер депозита в USDT:')
            bot.register_next_step_handler(msg, process_deposit)
            return
        if int(deposit) > 10000000:
            msg = bot.send_message(chat_id, 'Депозит не может быть больше 10.000.000 USDT\nУкажи размер депозита в USDT:')
            bot.register_next_step_handler(msg, process_deposit)
            return
        msg = bot.send_message(chat_id, 'Укажи риск в % для каждой сделки:')
        user = User(chat_id)
        user.deposit = deposit
        user_dict[chat_id] = user
        bot.register_next_step_handler(msg, process_risk)
    else:
        msg = bot.send_message(chat_id, 'Введённое значение должно быть числом!\nУкажи размер депозита в USDT:')
        bot.register_next_step_handler(msg, process_deposit)


def process_risk(message):
    chat_id = message.chat.id
    risk = message.text
    user = user_dict[chat_id]
    try:
        float(risk)
    except:
        msg = bot.send_message(chat_id, 'Введённое значение должно быть дробным числом (0.01 - 100.00)!\nУкажи риск в % для каждой сделки:')
        bot.register_next_step_handler(msg, process_risk)
        return
    if float(risk) < 0.01 or float(risk) > 100.00:
        msg = bot.send_message(chat_id,
                               'Введённое значение должно быть дробным числом (0.01 - 100.00)!\nУкажи риск в % для каждой сделки:')
        bot.register_next_step_handler(msg, process_risk)
        return
    user.risk = float(risk)
    db.register_user(chat_id, user.deposit, user.risk)
    bot.send_message(chat_id, 'Понял-принял!')
    bot.send_message(chat_id, 'Мы готовы к работе!', reply_markup=main_keyboard(chat_id))


def process_change_deposit(message):
    chat_id = message.chat.id
    deposit = message.text
    if deposit == '❌ Отмена':
        bot.send_message(chat_id, 'Меню: ', reply_markup=main_keyboard(chat_id))
        return
    if str(deposit).isnumeric():
        if int(deposit) < 100:
            msg = bot.send_message(chat_id, 'Депозит не может быть меньше 100 USDT\nУкажи размер депозита в USDT:',
                                   reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('❌ Отмена')))
            bot.register_next_step_handler(msg, process_change_deposit)
            return
        if int(deposit) > 10000000:
            msg = bot.send_message(chat_id, 'Депозит не может быть больше 10.000.000 USDT\nУкажи размер депозита в USDT:',
                                   reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('❌ Отмена')))
            bot.register_next_step_handler(msg, process_change_deposit)
            return
        db.change_deposit(chat_id, deposit)
        bot.send_message(chat_id, f'Успешно установлен новый депозит: {deposit} USDT\n\nМеню:', reply_markup=main_keyboard(chat_id))
    else:
        msg = bot.send_message(chat_id, 'Введённое значение должно быть числом!\nУкажи размер депозита в USDT:',
                               reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('❌ Отмена')))
        bot.register_next_step_handler(msg, process_change_deposit)


def change_deposit(message):
    chat_id = message.chat.id
    message = message.text
    if message == '✅ Да':
        msg = bot.send_message(chat_id, 'Укажи размер депозита в USDT:',
                               reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('❌ Отмена')))
        bot.register_next_step_handler(msg, process_change_deposit)
    else:
        bot.send_message(chat_id, 'Меню:', reply_markup=main_keyboard(chat_id))


def process_change_risk(message):
    chat_id = message.chat.id
    risk = message.text
    if risk == '❌ Отмена':
        bot.send_message(chat_id, 'Меню: ', reply_markup=main_keyboard(chat_id))
        return
    try:
        float(risk)
    except:
        msg = bot.send_message(chat_id, 'Введённое значение должно быть дробным числом (0.01 - 100.00)!\nУкажи риск в % для каждой сделки:',
                               reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('❌ Отмена')))
        bot.register_next_step_handler(msg, process_change_risk)
        return
    if float(risk) < 0.01 or float(risk) > 100.00:
        msg = bot.send_message(chat_id,
                               'Введённое значение должно быть дробным числом (0.01 - 100.00)!\nУкажи риск в % для каждой сделки:',
                               reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('❌ Отмена')))
        bot.register_next_step_handler(msg, process_change_risk)
        return
    db.change_risk(chat_id, risk)
    bot.send_message(chat_id, f'Установлен % риска: {risk}%.\n\nМеню:', reply_markup=main_keyboard(chat_id))


def change_risk(message):
    chat_id = message.chat.id
    message = message.text
    if message == '✅ Да':
        msg = bot.send_message(chat_id, 'Укажи риск в % для каждой сделки:',
                               reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('❌ Отмена')))
        bot.register_next_step_handler(msg, process_change_risk)
    else:
        bot.send_message(chat_id, 'Меню:', reply_markup=main_keyboard(chat_id))


def subscribe(message):
    chat_id = message.chat.id
    message = message.text
    if message == '✅ Да':
        db.unsubscribe(chat_id)
        bot.send_message(chat_id, 'Вы отписались.', reply_markup=main_keyboard(chat_id))
    else:
        bot.send_message(chat_id, 'Меню:', reply_markup=main_keyboard(chat_id))


@bot.message_handler(func=lambda message:True)
def all_messages(message):
    if message.text == "Депозит":
        deposit = db.get_deposit(message.chat.id)
        bot.send_message(message.chat.id, f'Указанный депозит: {deposit} USDT')
        msg = bot.send_message(message.chat.id, f'Желаешь поменять?',
                         reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('✅ Да'), KeyboardButton('❌ Нет')))
        bot.register_next_step_handler(msg, change_deposit)
    if message.text == "Риск":
        risk = db.get_risk(message.chat.id)
        bot.send_message(message.chat.id, f'Установленный риск: {risk}%')
        msg = bot.send_message(message.chat.id, f'Желаешь поменять?',
                         reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('✅ Да'), KeyboardButton('❌ Нет')))
        bot.register_next_step_handler(msg, change_risk)
    if message.text == 'Отписаться':
        msg = bot.send_message(message.chat.id, 'Вы уверены что хотите отписаться?',
                               reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('✅ Да'), KeyboardButton('❌ Нет')))
        bot.register_next_step_handler(msg, subscribe)
    if message.text == 'Подписаться':
        db.subscribe(message.chat.id)
        msg = bot.send_message(message.chat.id, 'Вы успешно подписались.', reply_markup=main_keyboard(message.chat.id))



bot.infinity_polling()