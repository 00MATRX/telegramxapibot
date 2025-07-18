from telegram.bot import bot
from config import TELEGRAM_USER_ID, MONTHLY_WRITE_CAP
from twitter.utils import track_usage

@bot.message_handler(commands=['usage'])
async def handle_usage(message):
    if message.from_user.id != TELEGRAM_USER_ID:
        return
    usage = track_usage()
    await bot.reply_to(message, f"Usage: {usage}/{MONTHLY_WRITE_CAP} posts this month.")
