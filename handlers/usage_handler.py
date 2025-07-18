from telegram.bot import bot
from config import TELEGRAM_USER_ID, MONTHLY_WRITE_CAP
from twitter.utils import track_usage
from handlers.base_handler import BaseHandler

class UsageHandler(BaseHandler):
    def __init__(self, bot, twitter_api):
        super().__init__(bot, twitter_api)

    async def handle_usage(self, message):
        if message.from_user.id != TELEGRAM_USER_ID:
            return
        usage = track_usage()
        await self.bot.reply_to(message, f"Usage: {usage}/{MONTHLY_WRITE_CAP} posts this month.")

def setup_usage_handler(bot, twitter_api):
    usage_handler = UsageHandler(bot, twitter_api)
    bot.register_message_handler(usage_handler.handle_usage, commands=['usage'])
    return usage_handler
