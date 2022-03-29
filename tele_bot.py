import telebot
from telebot import types
import requests

token = '5117488486:AAF0B4ugDyroUd5jaNXfWyhruHJAm8UNHc0'
bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Привет ✌️ ")

#
# bot.infinity_polling()


@bot.message_handler(commands=['start'])
def welcome(message):
    # sticker = open('static/sticker_welcome.webp', 'rb')
    # bot.send_sticker(message.chat.id, sticker)
    bot.send_message(message.chat.id, 'Привет!, {0.first_name}!\nЯ - {1.first_name})'.
                     format(message.from_user, bot.get_me()))


# @bot.send_message(message.chat.id, )
# @bot.message_handler(commands=['button'])
# def button_message(message):
#     markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     item1 = types.KeyboardButton("Кнопка")
#     markup.add(item1)
#     bot.send_message(message.chat.id, 'Выберите что вам надо', reply_markup=markup)
#
#
# bot.infinity_polling()


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == 'Привет':
        bot.send_message(message.from_user.id, 'Хочешь покажу волшебство? тогда напиши /reg')
        bot.register_next_step_handler(message, start)
    # elif message.text == 'Акции':
    #     bot.send_message(message.from_user.id, 'Введи тикер акции\n(например: BABA')
    #     bot.register_next_step_handler(message, investing)
    # elif message.text == 'Погода':
    #     bot.send_message(message.from_user.id, 'Введите название города на анг.яз\n(например: Moscow')
    #     bot.register_next_step_handler(message, weather)
    elif message.text == '/help':
        keyboard = types.InlineKeyboardMarkup()
        key_share = types.InlineKeyboardButton(text='Акции', callback_data='share')
        keyboard.add(key_share)
        key_weather = types.InlineKeyboardButton(text='Погода', callback_data='weather')
        keyboard.add(key_weather)
        key_weather = types.InlineKeyboardButton(text='Привет', callback_data='hello')
        keyboard.add(key_weather)
        question = 'Выбирай'
        return bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)
    else:
        bot.send_message(message.from_user.id, 'Я тебя не понимаю, напиши "/help.')


@bot.callback_query_handler(func=lambda call: True)
def callback_menu(call):
    try:
        if call.data == "share":  # call.data это callback_data, которую мы указали при объявлении кнопки
            bot.send_message(call.from_user.id, 'Введи тикер акции\nнапример: YNDX/TSLA/BIDU')
            bot.register_next_step_handler(call.message, investing)
        elif call.data == "weather":
            bot.send_message(call.message.from_user.id, 'Введи название города на анг.яз\nнапример: Moscow')
            bot.register_next_step_handler(call.message, weather)
        elif call.data == "hello":
            bot.send_message(call.message.from_user.id, 'Хочешь покажу волшебство? тогда напиши /reg')
            bot.register_next_step_handler(call.message, start)
    except AttributeError:
        bot.send_message(call.message.chat.id, 'Что?')
        bot.register_next_step_handler(call.message, get_text_messages)


name: str = ''
surname: str = ''
age: int = 0


@bot.message_handler(content_types=['text'])
def investing(message):
    try:
        ticker = message.text
        url = f"https://realstonks.p.rapidapi.com/{ticker}"

        headers = {
            "X-RapidAPI-Host": "realstonks.p.rapidapi.com",
            "X-RapidAPI-Key": "9df84d28aemsha55acca8940af39p183f27jsn1e9f343d7f58"
        }

        response = requests.request("GET", url, headers=headers)
        data = response.json()
        price = data['price']
        change_percentage = data['change_percentage']
        bot.send_message(message.from_user.id, f'{ticker} цена: {price} $\n'
                                               f'изменения: {change_percentage} %')
    except:
        bot.send_message(message.from_user.id, 'Я тебя не понимаю, напиши "/help.')


@bot.message_handler(content_types=['text'])
def weather(message):
    city = message.text
    url = "https://visual-crossing-weather.p.rapidapi.com/forecast"
    querystring = {"aggregateHours": "24", "location": city, "contentType": "json", "unitGroup": "uk",
                   "shortColumnNames": "0"}
    headers = {
        "X-RapidAPI-Host": "visual-crossing-weather.p.rapidapi.com",
        "X-RapidAPI-Key": "9df84d28aemsha55acca8940af39p183f27jsn1e9f343d7f58"
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    data = response.json()
    error = data['errorCode']
    if error == '999':
        bot.send_message(message.from_user.id, 'У меня нет данных.\n Уточните название города')
        bot.register_next_step_handler(message, weather)
    else:
        temperature = data['locations'][city]['currentConditions']['temp']
        precip = data['locations'][city]['currentConditions']['precip']
        humidity = data['locations'][city]['currentConditions']['temp']
        wind_direction = data['locations'][city]['currentConditions']['wdir']
        wind_speed = data['locations'][city]['currentConditions']['wspd']

        def precipitation(precip):
            if precip is None:
                return 'без осадков'
            else:
                return precip

        def wind_dir(wind_direction):
            data = int(wind_direction)
            res = (round((data / 22.5 + 0.5), 0)) % 16
            arr = ["северный", "ССВ", "северо-восточный", "ВСВ", "восточный", "ВЮВ", "юго-восточный", "ЮЮВ", "южный",
                   "ЗЗЮ",
                   "юго-западный", "ВЮВ", "западный", "ЗСЗ", "северо-западный", "ССЗ"]
            for index, value in enumerate(arr):
                if res == index:
                    return value

        w_direction = wind_dir(wind_direction)
        precipitations = precipitation(precip)
        bot.send_message(message.from_user.id, f"""
                                                город: {city}
                                                температура:{temperature} С
                                                осадки: {precipitations}
                                                влажность: {humidity}%
                                                направление ветра: {w_direction}
                                                скорость ветра: {wind_speed} м\\с""")


@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == '/reg':
        bot.send_message(message.from_user.id, 'Как тебя зовут?')
        bot.register_next_step_handler(message, get_name)
    else:
        bot.send_message(message.from_user.id, 'Напиши /reg')


def get_name(message):
    global name
    name = message.text
    bot.send_message(message.from_user.id, 'А фамилия')
    bot.register_next_step_handler(message, get_surname)


def get_surname(message):
    global surname
    surname = message.text
    bot.send_message(message.from_user.id, 'А возраст')
    bot.register_next_step_handler(message, get_age)


def get_age(message):
    global age
    while age == 0:
        try:
            age = int(message.text)
        except Exception:
            bot.send_message(message.from_user.id, 'Цифрами, пожалуйста')
    # bot.send_message(message.from_user.id, f'Тебе {age} лет, тебя зовут {name} {surname}')
    keyboard = types.ReplyKeyboardMarkup()  # наша клавиатура
    key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')  # кнопка «Да»
    keyboard.add(key_yes)  # добавляем кнопку в клавиатуру
    key_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard.add(key_no)
    question = 'Тебе ' + str(age) + ' лет, тебя зовут ' + name + ' ' + surname + '?'

    return bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    try:
        if call.data == "yes":  # call.data это callback_data, которую мы указали при объявлении кнопки
            bot.send_message(call.message.chat.id, f'Я тебя запомнил: Имя: {name} фамилия: {surname} возраст: {age})')
        elif call.data == "no":
            bot.register_next_step_handler(call.message.chat.id, start)
    except AttributeError:
        bot.send_message(call.message.chat.id, 'Что?')
        bot.register_next_step_handler(call.message, get_text_messages)


# bot.polling(none_stop=True, interval=0)
if __name__ == '__main__':
    bot.infinity_polling()
