import asyncio
import logging
from telegram.bot import telegram_bot
from twitter.api import twitter_api
from handlers.start_handler import setup_start_handler
from handlers.tweet_handler import setup_tweet_handler
from handlers.schedule_handler import setup_schedule_handler
from handlers.usage_handler import setup_usage_handler
from twitter.utils import track_usage

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def main():
    bot = telegram_bot.bot

    start_handler = setup_start_handler(bot, twitter_api)
    await start_handler.set_commands()

    setup_tweet_handler(bot, twitter_api)
    schedule_handler = setup_schedule_handler(bot, twitter_api)
    setup_usage_handler(bot, twitter_api)

    logging.info("Starting async polling...")
    asyncio.create_task(asyncio.to_thread(schedule_handler.run_scheduler))
    await bot.infinity_polling()

if __name__ == "__main__":
    track_usage()
    asyncio.run(main())
