import logging
import os
from tempfile import NamedTemporaryFile

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReactionTypeEmoji

from config import TELEGRAM_USER_ID
from handlers.base_handler import BaseHandler
from twitter.utils import post_tweet_with_media, download_media

logger = logging.getLogger(__name__)

class TweetHandler(BaseHandler):
    def __init__(self, bot, twitter_api):
        super().__init__(bot, twitter_api)

    async def handle_text(self, message):
        if message.from_user.id != TELEGRAM_USER_ID:
            return
        text = message.text
        if text == "📝 Post Text":
            await self.bot.reply_to(message, "Enter text to post:")
            return
        elif text == "💬 Reply to Tweet":
            await self.bot.reply_to(message, "Enter tweet ID and text (ID text):")
            return
        elif text == "⏰ Schedule Post":
            await self.bot.reply_to(message, "Enter mins and text (mins text):")
            return
        elif text == "📊 Check Usage":
            from handlers.usage_handler import UsageHandler
            usage_handler = UsageHandler(self.bot, self.twitter_api)
            await usage_handler.handle_usage(message)
            return
        else:
            await self.confirm_post(message, text)

    async def handle_media(self, message):
        if message.from_user.id != TELEGRAM_USER_ID:
            return
        text = message.caption or "Media tweet"
        media_paths = []
        try:
            if message.photo:
                file_id = message.photo[-1].file_id
                ext = '.jpg'
            elif message.video:
                file_id = message.video.file_id
                ext = '.mp4'
            elif message.animation:
                file_id = message.animation.file_id
                ext = '.gif'
            else:
                return

            file_info = await self.bot.get_file(file_id)
            file_url = f"https://api.telegram.org/file/bot{self.bot.token}/{file_info.file_path}"
            content = await download_media(file_url)

            with NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
                temp_file.write(content)
                media_paths.append(temp_file.name)

            await self.confirm_post(message, text, media_paths=media_paths)
        except Exception as e:
            logger.exception("Error handling media message: %s", e)
            await self.bot.reply_to(message, f"Error: {str(e)}")
            await self.bot.send_message(TELEGRAM_USER_ID, f"Alert: {str(e)}")
        finally:
            for path in media_paths:
                if os.path.exists(path):
                    os.unlink(path)

    async def confirm_post(self, message, text, media_paths=None, reply_to_id=None):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("✅ Confirm", callback_data=f"confirm:{reply_to_id or ''}:{message.message_id}"))
        markup.add(InlineKeyboardButton("🗑 Cancel", callback_data="cancel"))
        await self.bot.reply_to(message, f"Preview: {text}", reply_markup=markup)

    async def handle_callback(self, call):
        if call.from_user.id != TELEGRAM_USER_ID:
            return
        data = call.data
        if data.startswith("confirm:"):
            parts = data.split(":")
            reply_id = parts[1] if parts[1] else None
            try:
                await post_tweet_with_media(call.message.text.replace("Preview: ", ""), reply_to_id=reply_id)
                await self.bot.answer_callback_query(call.id, "Posted!")
                await self.bot.edit_message_text("Posted successfully!", call.message.chat.id, call.message.message_id)
                await self.bot.set_message_reaction(call.message.chat.id, call.message.message_id, [ReactionTypeEmoji(type="emoji", emoji="👍")])
            except Exception as e:
                logger.exception("Error posting tweet: %s", e)
                await self.bot.answer_callback_query(call.id, f"Error: {str(e)}")
        elif data == "cancel":
            await self.bot.answer_callback_query(call.id, "Cancelled.")
            await self.bot.delete_message(call.message.chat.id, call.message.message_id)

    async def handle_reply(self, message):
        if message.from_user.id != TELEGRAM_USER_ID:
            return
        parts = message.text.split(maxsplit=2)
        if len(parts) < 3:
            await self.bot.reply_to(message, "Usage: /reply <tweet_id> <text>")
            return
        reply_id, text = parts[1], parts[2]
        await self.confirm_post(message, text, reply_to_id=reply_id)

def setup_tweet_handler(bot, twitter_api):
    tweet_handler = TweetHandler(bot, twitter_api)
    bot.register_message_handler(tweet_handler.handle_text, content_types=['text'])
    bot.register_message_handler(tweet_handler.handle_media, content_types=['photo', 'video', 'animation'])
    bot.register_callback_query_handler(tweet_handler.handle_callback, func=lambda call: True)
    bot.register_message_handler(tweet_handler.handle_reply, commands=['reply'])
