from telebot.types import ReplyKeyboardMarkup, KeyboardButton, BotCommand
from telegram.bot import bot
from config import TELEGRAM_USER_ID

async def set_commands():
    commands = [
        BotCommand("start", "Start the bot with menu"),
        BotCommand("reply", "Reply to a tweet"),
        BotCommand("schedule", "Schedule a post"),
        BotCommand("usage", "Check monthly usage")
    ]
    await bot.set_my_commands(commands)

@bot.message_handler(commands=['start'])
async def send_welcome(message):
    if message.from_user.id != TELEGRAM_USER_ID:
        await bot.reply_to(message, "Unauthorized.")
        return
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    markup.add(KeyboardButton("📝 Post Text"))
    markup.add(KeyboardButton("🎥 Post Video"), KeyboardButton("🖼 Post Photo"))
    markup.add(KeyboardButton("💬 Reply to Tweet"), KeyboardButton("⏰ Schedule Post"))
    markup.add(KeyboardButton("📊 Check Usage"))
    await bot.reply_to(message, "Advanced bot ready! Tap buttons below.", reply_markup=markup)
