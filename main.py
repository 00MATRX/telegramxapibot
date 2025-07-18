import asyncio
import logging
from telegram.bot import bot
from handlers.start_handler import set_commands
from handlers.tweet_handler import handle_text, handle_callback
from handlers.reply_handler import handle_reply, handle_reply_button
from handlers.media_handler import handle_media, handle_media_button
from handlers.schedule_handler import handle_schedule, run_scheduler
from handlers.usage_handler import handle_usage
from twitter.api import client, api

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def main():
    await set_commands()
    logging.info("Starting async polling...")
    asyncio.create_task(asyncio.to_thread(run_scheduler, client, api, bot))
    await bot.infinity_polling()

if __name__ == "__main__":
    track_usage()
    asyncio.run(main())
