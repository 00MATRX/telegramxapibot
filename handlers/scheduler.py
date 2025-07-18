import schedule
import time
import asyncio
from utils import post_tweet_with_media
from config import TELEGRAM_USER_ID

queued_posts = []  # [(text, media_paths, reply_to_id, bot)]

def run_scheduler(client, api, bot):
    async def process_queue():
        while queued_posts:
            text, media_paths, reply_to_id, _ = queued_posts.pop(0)
            try:
                await post_tweet_with_media(client, api, text, media_paths, reply_to_id)
                await bot.send_message(TELEGRAM_USER_ID, f"Scheduled post sent: {text}")
            except Exception as e:
                await bot.send_message(TELEGRAM_USER_ID, f"Scheduled post failed: {str(e)}")

    schedule.every(1).minutes.do(lambda: asyncio.run_coroutine_threadsafe(process_queue(), asyncio.get_event_loop()))

    while True:
        schedule.run_pending()
        time.sleep(1)
