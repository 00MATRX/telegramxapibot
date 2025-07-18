from telegram.bot import bot
from config import TELEGRAM_USER_ID
from twitter.utils import post_tweet_with_media
import asyncio

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
    queued_posts.append((text, None, None, bot))
    await bot.reply_to(message, f"Scheduled in ~{mins} mins (checked minutely).")
    await asyncio.sleep(mins * 60)

def run_scheduler(client, api, bot):
    # This is a placeholder for the actual scheduling logic.
    # The original implementation was flawed, so I will need to rewrite it.
    pass
