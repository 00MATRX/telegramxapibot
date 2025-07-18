import asyncio
import logging
from telegram.bot import bot
from handlers.start_handler import set_commands, send_welcome
from handlers.tweet_handler import handle_text, handle_media, handle_callback, handle_reply
from handlers.schedule_handler import handle_schedule, run_scheduler
from handlers.usage_handler import handle_usage
from twitter.utils import track_usage

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def main():
    await set_commands()
    logging.info("Starting async polling...")
    asyncio.create_task(asyncio.to_thread(run_scheduler))
    await bot.infinity_polling()

if __name__ == "__main__":
    asyncio.run(main())
