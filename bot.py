import telebot
from config import token
import requests

bot = telebot.TeleBot()
 # Ф-ция получения курса валют
def get_currency_rates():
    response = requests.get("dec30d83130b43e3aafa07d37c95b6e7")
    data = response.json()
    return data
# Обработчик сообщений старт
@bot.message_handler(commands=['start', 'help'])
# Ф-ция приветствия
def send_welcome(message):
    bot.reply_to(message,"Привет! Я бот, который помогает тебе отслеживать курсы валют.")
@bot.message_handler(commands=['rate'])
def send_rates(message):
    rates =get_currency_rates()
    reply = f"Курс USD: {rates['USD']}\nКурс EUR: {rates['EUR']}"
    bot.reply_to(message,reply)
bot.polling()



