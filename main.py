import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import os
import dbo as db_

API_TOKEN = '5162882119:AAEzXwekU3IKXWGJdt9BEkxh4yzk1pLN0TE'

bot = telebot.TeleBot(API_TOKEN)
db = db_.database()

user_dict = {}
channel = -1001263015690


class User:
    def __init__(self, id):
        self.id = id
        self.deposit = 0
        self.risk = 0


class Signal:
    def __init__(self):
        self.token = ''
        self.shortlong = ''
        self.entry_min = 0
        self.entry_max = 0
        self.goal = 0
        self.stop = 0
        self.percentstop = 0


sign = Signal()


def main_keyboard(id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton('Риск'), KeyboardButton('Депозит'))
    if db.get_sub(id):
        markup.add(KeyboardButton('Отписаться'))
    else:
        markup.add(KeyboardButton('Подписаться'))
    if db.isadmin(id):
        markup.add(KeyboardButton('Админка'))
    return markup


@bot.message_handler(commands=['start'])
def send_welcome(message):
    id = message.chat.id
    user = db.check_user(id)
    if len(user) == 0:
        try:
            bot.send_message(id, '''
BS BOT на связи!
        
Я буду твоим верным помощником в торговле.
        
Но для начала, укажи свой депозит и риск для сделок!
        ''')
            msg = bot.send_message(id, 'Укажи размер депозита в USDT:')
            bot.register_next_step_handler(msg, process_deposit)
        except:
            pass
    else:
        try:
            bot.send_message(id, 'Меню: ', reply_markup=main_keyboard(id))
        except:
            pass


def process_deposit(message):
    chat_id = message.chat.id
    deposit = message.text
    if str(deposit).isnumeric():
        if int(deposit) < 100:
            try:
                msg = bot.send_message(chat_id, 'Депозит не может быть меньше 100 USDT\nУкажи размер депозита в USDT:')
            except:
                return
            bot.register_next_step_handler(msg, process_deposit)
            return
        if int(deposit) > 10000000:
            try:
                msg = bot.send_message(chat_id, 'Депозит не может быть больше 10.000.000 USDT\nУкажи размер депозита в USDT:')
            except:
                return
            bot.register_next_step_handler(msg, process_deposit)
            return
        try:
            msg = bot.send_message(chat_id, 'Укажи риск в % для каждой сделки:')
        except:
            return
        user = User(chat_id)
        user.deposit = deposit
        user_dict[chat_id] = user
        bot.register_next_step_handler(msg, process_risk)
    else:
        try:
            msg = bot.send_message(chat_id, 'Введённое значение должно быть числом!\nУкажи размер депозита в USDT:')
        except:
            return
        bot.register_next_step_handler(msg, process_deposit)


def process_risk(message):
    chat_id = message.chat.id
    risk = message.text
    user = user_dict[chat_id]
    try:
        float(risk)
    except:
        try:
            msg = bot.send_message(chat_id, 'Введённое значение должно быть дробным числом (0.01 - 100.00)!\nУкажи риск в % для каждой сделки:')
        except:
            return
        bot.register_next_step_handler(msg, process_risk)
        return
    if float(risk) < 0.01 or float(risk) > 100.00:
        try:
            msg = bot.send_message(chat_id,
                               'Введённое значение должно быть дробным числом (0.01 - 100.00)!\nУкажи риск в % для каждой сделки:')
        except:
            return
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


def process_input_percentstop(message):
    if message.text == 'Отмена':
        bot.send_message(message.chat.id, 'Меню:', reply_markup=main_keyboard(message.chat.id))
        return
    bot.send_message(message.chat.id, 'Готово.', reply_markup=main_keyboard(message.chat.id))
    sign.percentstop = message.text
    percentstop = round(float(sign.percentstop), 2)
    if float(sign.percentstop) > 0:
        percentstop = float(sign.percentstop) * -1
        percentstop = round(percentstop, 2)
    msg = bot.send_message(channel, f'{sign.token} - FUTURES - {sign.shortlong}\n\n'
                                      f'Вход: {sign.entry_min} - {sign.entry_max}\n\n'
                                      f'Цель: {sign.goal}\n\n'
                                      f'СТОП: {sign.stop} ({percentstop}%)')
    for user in db.get_users():
        try:
            bot.send_message(user[0], msg.text, reply_markup=main_keyboard(user[0]))
        except Exception as e:
            continue
        try:
            calc = (float(user[1]) / float(sign.percentstop)) * float(user[2])
            calc = round(calc, 2)
            if calc < 0:
                calc = calc * -1
            bot.send_message(user[0], f'Расчёт: {calc}$')
        except Exception as e:
            print(e)


def process_input_stop(message):
    if message.text == 'Отмена':
        bot.send_message(message.chat.id, 'Меню:', reply_markup=main_keyboard(message.chat.id))
        return
    sign.stop = message.text
    msg = bot.send_message(message.chat.id, 'Введите % стоп:')
    bot.register_next_step_handler(msg, process_input_percentstop)


def process_input_goal(message):
    if message.text == 'Отмена':
        bot.send_message(message.chat.id, 'Меню:', reply_markup=main_keyboard(message.chat.id))
        return
    sign.goal = message.text
    msg = bot.send_message(message.chat.id, 'Введите стоп:')
    bot.register_next_step_handler(msg, process_input_stop)


def process_input_entry_max(message):
    if message.text == 'Отмена':
        bot.send_message(message.chat.id, 'Меню:', reply_markup=main_keyboard(message.chat.id))
        return
    sign.entry_max = message.text
    msg = bot.send_message(message.chat.id, 'Введите цель:')
    bot.register_next_step_handler(msg, process_input_goal)


def process_input_entry_min(message):
    if message.text == 'Отмена':
        bot.send_message(message.chat.id, 'Меню:', reply_markup=main_keyboard(message.chat.id))
        return
    sign.entry_min = message.text
    msg = bot.send_message(message.chat.id, 'Введите вход(макс):')
    bot.register_next_step_handler(msg, process_input_entry_max)


def process_input_shortlong(message):
    if message.text == 'Отмена':
        bot.send_message(message.chat.id, 'Меню:', reply_markup=main_keyboard(message.chat.id))
        return
    sign.shortlong = message.text
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Отмена')
    msg = bot.send_message(message.chat.id, 'Введите вход(мин):', reply_markup=markup)
    bot.register_next_step_handler(msg, process_input_entry_min)


def process_input_token(message):
    if message.text == 'Отмена':
        bot.send_message(message.chat.id, 'Меню:', reply_markup=main_keyboard(message.chat.id))
        return
    sign.token = message.text
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('SHORT', 'LONG')
    markup.add('Отмена')
    msg = bot.send_message(message.chat.id, 'Выберите SHORT/LONG:', reply_markup=markup)
    bot.register_next_step_handler(msg, process_input_shortlong)


def adminmenu(message):
    if message.text == 'Добавить сигнал':
        msg = bot.send_message(message.chat.id, 'Введите токен:',
                               reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add('Отмена'))
        bot.register_next_step_handler(msg, process_input_token)
    else:
        bot.send_message(message.chat.id, 'Меню:', reply_markup=main_keyboard(message.chat.id))
        return


@bot.message_handler(func=lambda message:True)
def all_messages(message):
    if message.text == "Админка" and db.isadmin(message.chat.id):
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('Добавить сигнал')
        markup.add('Отмена')
        msg = bot.send_message(message.chat.id, 'Админ меню:', reply_markup=markup)
        bot.register_next_step_handler(msg, adminmenu)
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