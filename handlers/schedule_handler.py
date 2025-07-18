from telegram.bot import bot
from config import TELEGRAM_USER_ID
from twitter.utils import post_tweet_with_media
import asyncio
import schedule
import time

queued_posts = []

@bot.message_handler(commands=['schedule'])
async def handle_schedule(message):
    if message.from_user.id != TELEGRAM_USER_ID:
        return
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await bot.reply_to(message, "Usage: /schedule <mins> <text>")
        return
    mins = int(parts[1])
    text = parts[2]

    # Schedule the post
    schedule.every(mins).minutes.do(post_scheduled_tweet, text=text)

    await bot.reply_to(message, f"Scheduled in ~{mins} mins.")

def post_scheduled_tweet(text):
    asyncio.run(post_tweet_with_media(text))

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)
