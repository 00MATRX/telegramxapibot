from telebot.types import ReplyKeyboardMarkup, KeyboardButton, BotCommand
from telegram.bot import bot
from config import TELEGRAM_USER_ID
from handlers.base_handler import BaseHandler

class StartHandler(BaseHandler):
    def __init__(self, bot, twitter_api):
        super().__init__(bot, twitter_api)

    async def set_commands(self):
        commands = [
            BotCommand("start", "Start the bot with menu"),
            BotCommand("reply", "Reply to a tweet"),
            BotCommand("schedule", "Schedule a post"),
            BotCommand("usage", "Check monthly usage")
        ]
        await self.bot.set_my_commands(commands)

    async def send_welcome(self, message):
        if message.from_user.id != TELEGRAM_USER_ID:
            await self.bot.reply_to(message, "Unauthorized.")
            return
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        markup.add(KeyboardButton("📝 Post Text"))
        markup.add(KeyboardButton("🎥 Post Video"), KeyboardButton("🖼 Post Photo"))
        markup.add(KeyboardButton("💬 Reply to Tweet"), KeyboardButton("⏰ Schedule Post"))
        markup.add(KeyboardButton("📊 Check Usage"))
        await self.bot.reply_to(message, "Advanced bot ready! Tap buttons below.", reply_markup=markup)

def setup_start_handler(bot, twitter_api):
    start_handler = StartHandler(bot, twitter_api)
    bot.register_message_handler(start_handler.send_welcome, commands=['start'])
    return start_handler
