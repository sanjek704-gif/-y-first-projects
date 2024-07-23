import telebot
from config import token
from telebot import types
import requests

# Инициализация бота с токеном
bot = telebot.TeleBot(token)
cash = 0

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет! Введите сумму конвертации:')
    bot.register_next_step_handler(message, get_amount)

# Получение суммы конвертации
def get_amount(message):
    global cash

    try:
        cash = float(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, 'Неверный формат. Введите числовое значение.')
        bot.register_next_step_handler(message, get_amount)
        return

    if cash > 0:
        markup = types.InlineKeyboardMarkup(row_width=2) # Создание кнопок выбора валютной пары
        btn1 = types.InlineKeyboardButton("USD/BYN", callback_data="usd/byn")
        btn2 = types.InlineKeyboardButton("EUR/BYN", callback_data="eur/byn")
        btn3 = types.InlineKeyboardButton("USD/RUB", callback_data="usd/rub")
        btn4 = types.InlineKeyboardButton("Другое", callback_data="else")
        markup.add(btn1, btn2, btn3, btn4)
        bot.send_message(message.chat.id, 'Выберите пару валют:', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Введите число больше 0.')
        bot.register_next_step_handler(message, get_amount)

# Обработчик выбора валютной пары
@bot.callback_query_handler(func=lambda call: True)
def callback_message(call):
    if call.data != 'else':
        val = call.data.upper().split('/')
        url = f'https://v6.exchangerate-api.com/v6/6ed013d81816a9fb77ae4284/latest/{val[0]}'
        response = requests.get(url)
        data = response.json()
        if 'conversion_rates' in data:
            valuta = val[1]
            rate = data['conversion_rates'][valuta]
            res = cash * rate
            bot.send_message(call.message.chat.id, f'Итог: *{round(res, 2)}* {valuta}\nКурс перевода: {rate} для пары валют {val[0]}/{val[1]}\n'
                                                   f'Введите сумму новой конвертации:', parse_mode= "Markdown" )
        else:
            bot.send_message(call.message.chat.id, 'Произошла ошибка при получении данных. Попробуйте позже.')
        bot.register_next_step_handler(call.message, get_amount)
    else:
        bot.send_message(call.message.chat.id, 'Введите валютную пару (например, usd/eur):')
        bot.register_next_step_handler(call.message, custom_currency)

# Обработчик ввода пользовательской валютной пары
def custom_currency(message):
    try:
        val = message.text.upper().split('/')
        url = f'https://v6.exchangerate-api.com/v6/6ed013d81816a9fb77ae4284/latest/{val[0]}'
        response = requests.get(url)
        data = response.json()
        if 'conversion_rates' in data:
            valuta = val[1]
            rate = data['conversion_rates'][valuta]
            res = cash * rate
            bot.send_message(message.chat.id, f'Итог: *{round(res, 2)}* {valuta}\nКурс перевода: {rate} для пары валют {val[0]}/{val[1]}\n'
                                              f'Введите сумму для новой конвертации:',parse_mode= "Markdown")
        else:
            bot.send_message(message.chat.id, 'Произошла ошибка при получении данных. Попробуйте позже.')
    except Exception as e:
        bot.send_message(message.chat.id, f'Ошибка: {e}\nПожалуйста, проверьте правильность введенных данных.')
    bot.register_next_step_handler(message, get_amount)

# Запуск бота
bot.polling()
