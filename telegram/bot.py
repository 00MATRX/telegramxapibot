from telebot.async_telebot import AsyncTeleBot
from config import TELEGRAM_TOKEN

class TelegramBot:
    def __init__(self, token):
        self.bot = AsyncTeleBot(token)

telegram_bot = TelegramBot(TELEGRAM_TOKEN)
bot = telegram_bot.bot
