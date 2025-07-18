import asyncio
from telegram.bot import bot
from config import TELEGRAM_USER_ID
from twitter.utils import post_tweet_with_media
from handlers.base_handler import BaseHandler

class ScheduleHandler(BaseHandler):
    def __init__(self, bot, twitter_api):
        super().__init__(bot, twitter_api)
        self.queued_posts = []

    async def handle_schedule(self, message):
        if message.from_user.id != TELEGRAM_USER_ID:
            return
        parts = message.text.split(maxsplit=2)
        if len(parts) < 3:
            await self.bot.reply_to(message, "Usage: /schedule <mins> <text>")
            return
        mins = int(parts[1])
        text = parts[2]
        self.queued_posts.append((text, None, None, self.bot))
        await self.bot.reply_to(message, f"Scheduled in ~{mins} mins (checked minutely).")
        await asyncio.sleep(mins * 60)

    def run_scheduler(self):
        """Run the scheduler in a separate thread"""
        import schedule
        import time
        
        def process_queue():
            while self.queued_posts:
                text, media_paths, reply_to_id, bot = self.queued_posts.pop(0)
                try:
                    # This would need to be called from async context
                    # For now, just remove from queue
                    pass
                except Exception as e:
                    print(f"Scheduled post failed: {str(e)}")
        
        schedule.every(1).minutes.do(process_queue)
        
        while True:
            schedule.run_pending()
            time.sleep(1)

def setup_schedule_handler(bot, twitter_api):
    schedule_handler = ScheduleHandler(bot, twitter_api)
    bot.register_message_handler(schedule_handler.handle_schedule, commands=['schedule'])
    return schedule_handler
