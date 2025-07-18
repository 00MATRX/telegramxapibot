from telegram.bot import bot
from config import TELEGRAM_USER_ID
from handlers.tweet_handler import confirm_post

@bot.message_handler(commands=['reply'])
async def handle_reply(message):
    if message.from_user.id != TELEGRAM_USER_ID:
        return
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await bot.reply_to(message, "Usage: /reply <tweet_id> <text>")
        return
    reply_id, text = parts[1], parts[2]
    await confirm_post(message, text, reply_to_id=reply_id)

@bot.message_handler(func=lambda message: message.text == "💬 Reply to Tweet")
async def handle_reply_button(message):
    if message.from_user.id != TELEGRAM_USER_ID:
        return
    await bot.reply_to(message, "Enter tweet ID and text (ID text):")
