# -*- coding: utf-8 -*-

#Production by Famaxth
#Telegram - @por0vos1k


import db
import telebot
import config
import app_logger
from telebot import types
from bad_words import bad_words


user0 = config.admin_id

bot = telebot.TeleBot(config.token, parse_mode='HTML')

bot_info = bot.get_me()

logger = app_logger.get_logger(__name__)

logger.info('Бот начал работу!', name='Bot')

db.init_db()


def foo(item):
    return item[0]


def scan_message(text):
    result = None
    for symbol in bad_words:
        if symbol in text:
            result = symbol
    return result



def start_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    but_1 = types.InlineKeyboardButton(text="Разработчик", callback_data="Разработчик")
    but_2 = types.InlineKeyboardButton(text="Группа с новостями", url=config.group)
    keyboard.row(but_1)
    keyboard.row(but_2)
    return keyboard



@bot.message_handler(commands=['start'])
def bot_command_start(message):
    if message.chat.type == 'private':
        keyboard = start_keyboard()
        bot.send_message(message.chat.id, "<a>Привет!\nЯ <b>AntiArabBot</b> - Бот, который следит за порядком в твоем чате.\n<b>Ни один араб мимо меня не пройдет!</b>\n\nЧтобы узнать о всех моих функциях — пиши /help.</a>", parse_mode = 'HTML', reply_markup=keyboard)



@bot.message_handler(commands=['help'])
def bot_command_help(message):
    if message.chat.type == 'private':
        keyboard = types.InlineKeyboardMarkup()
        but_1 = types.InlineKeyboardButton(text="Главное Меню", callback_data="Главное Меню")
        keyboard.row(but_1)
        bot.send_message(message.chat.id, """<a><b>Часто администраторы сталкиваются со спамом, чтобы справляться с такой проблемой, нужно прибегать к высшим силам, для этого есть я.</b>\n\nДля чего я сделан:\nБот сделан исключительно для устранения спама от "арабов". Мои функции помогут защитить чат от аккаунтов, но не от ботов.\n\nЧто я умею: \n1. Удаляю сообщения с содержанием арабских иероглифов, именно такие символы часто используют спамеры.\n2: Блокирую пользователей с арабскими именами, здесь аналогичная ситуация.\n\n\nЧто для этого нужно: \nТебе достаточно просто добавить меня в группу и чтобы меня активировать, нужно выдать мне права на удаления сообщений и на блокировку пользователей в вашем чате. И после этих всех действий — я с радостью начну работать во благо чата.</a>""", parse_mode = 'HTML', reply_markup = keyboard)



@bot.message_handler(content_types=['new_chat_members'])
def greeting(message):
    if message.from_user.id != user0:
        black_list = db.return_black_list()
        try:
            blacklist = list(foo, black_list)
        except Exception as e:
            print(e)
        if str(message.from_user.id) not in black_list:
            try:
                if message.from_user.first_name or message.from_user.last_name not in bad_words:
                    print("New chat member")
                else:
                    db.add_user(message.from_user.first_name, message.from_user.last_name, message.from_user.id)
                    bot.send_message(message.chat.id, "Мы удалили из чата ХХХ араба @{}.\nТут не приветствуются Арабы!".format(message.from_user.username), parse_mode='HTML')
                    bot.kick_chat_member(message.chat.id, message.from_user.id)
            except Exception as e:
                print(e)

        else:
            bot.kick_chat_member(message.chat.id, message.from_user.id)



@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        keyboard = types.InlineKeyboardMarkup()
        but_1 = types.InlineKeyboardButton(text="Главное Меню", callback_data="Главное Меню")
        keyboard.row(but_1)
        if call.data == 'Разработчик':
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="По всем вопросам и предложениям писать: @por0vos1k", reply_markup=keyboard)
        elif call.data == 'Главное Меню':
            keyboard = start_keyboard()
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="<a>Привет!\nЯ <b>AntiArabBot</b> - Бот, который следит за порядком в твоем чате.\n<b>Ни один араб мимо меня не пройдет!</b>\n\nЧтобы узнать о всех моих функциях — пиши /help.</a>", parse_mode = 'HTML', reply_markup=keyboard)



@bot.message_handler(content_types=config.all_content_types)
def bot_new_message(message):
    if message.text:
        text_save = message.text
    elif message.caption:
        text_save = message.caption
    else:
        text_save = None
    if not text_save:
        return
    text = text_save.translate(config.regexp).lower()
    text = config.emoji_pattern.sub(r'', text).split(' ')
    for word in text:
        result = scan_message(word)
        if result:
            bot.delete_message(message.chat.id, message.message_id)
            if message.from_user.id != user0:
                db.add_user(str(message.from_user.first_name), str(message.from_user.last_name), int(message.from_user.id))
                bot.send_message(message.chat.id, "Мы удалили из чата ХХХ араба @{}.\nТут не приветствуются Арабы!".format(message.from_user.username), parse_mode='HTML')
                bot.kick_chat_member(message.chat.id, message.from_user.id)



@bot.message_handler(content_types=['new_chat_members'])
def bot_join(message):
    for user in message.new_chat_members:
        if user.id == bot_info.id:
            logger.info(f'Пригласили в группу {message.chat.title}', name=message.from_user.first_name)



@bot.message_handler(content_types=['left_chat_member'])
def bot_left(message):
    user = message.left_chat_member
    if user.id == bot_info.id:
        logger.info(f'Выкинули из группы {message.chat.title}', name=message.from_user.first_name)



if __name__ == '__main__':
    bot.polling(none_stop=True)


logger.info('Бот закончил работу!', name='Bot')
