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

        try:
            media_path = None
            if message.photo:
                file_id = message.photo[-1].file_id
                media_path = await download_media(self.bot, file_id, "photo")
            elif message.video:
                file_id = message.video.file_id
                media_path = await download_media(self.bot, file_id, "video")
            elif message.animation:
                file_id = message.animation.file_id
                media_path = await download_media(self.bot, file_id, "animation")

            if media_path:
                caption = message.caption or ""
                await self.confirm_media_post(message, caption, media_path)
        except Exception as e:
            await self.bot.reply_to(message, f"Error processing media: {str(e)}")

    async def handle_reply(self, message):
        if message.from_user.id != TELEGRAM_USER_ID:
            return

        parts = message.text.split(maxsplit=2)
        if len(parts) < 3:
            await self.bot.reply_to(message, "Usage: /reply <tweet_id> <text>")
            return

        tweet_id = parts[1]
        text = parts[2]

        try:
            await post_tweet_with_media(self.twitter_api, text, None, reply_to_id=tweet_id)
            await self.bot.reply_to(message, "Reply posted successfully!")
        except Exception as e:
            await self.bot.reply_to(message, f"Error posting reply: {str(e)}")

    async def confirm_post(self, message, text):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("✅ Post", callback_data=f"post_text:{text}"))
        markup.add(InlineKeyboardButton("❌ Cancel", callback_data="cancel"))
        await self.bot.reply_to(message, f"Confirm post:\n\n{text}", reply_markup=markup)

    async def confirm_media_post(self, message, caption, media_path):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("✅ Post", callback_data=f"post_media:{caption}:{media_path}"))
        markup.add(InlineKeyboardButton("❌ Cancel", callback_data="cancel"))
        await self.bot.reply_to(message, f"Confirm media post:\n\n{caption}", reply_markup=markup)

    async def handle_callback(self, call):
        if call.from_user.id != TELEGRAM_USER_ID:
            return

        if call.data == "cancel":
            await self.bot.answer_callback_query(call.id, "Cancelled")
            await self.bot.edit_message_text("Cancelled", call.message.chat.id, call.message.message_id)
            return

        if call.data.startswith("post_text:"):
            text = call.data[10:]  # Remove "post_text:" prefix
            try:
                await post_tweet_with_media(self.twitter_api, text, None)
                await self.bot.answer_callback_query(call.id, "Posted!")
                await self.bot.edit_message_text("✅ Posted successfully!", call.message.chat.id, call.message.message_id)
                await self.bot.set_message_reaction(call.message.chat.id, call.message.message_id, [ReactionTypeEmoji("✅")])
            except Exception as e:
                await self.bot.answer_callback_query(call.id, f"Error: {str(e)}")
                await self.bot.edit_message_text(f"❌ Error: {str(e)}", call.message.chat.id, call.message.message_id)

        elif call.data.startswith("post_media:"):
            parts = call.data[11:].split(":", 1)  # Remove "post_media:" prefix
            caption = parts[0] if parts[0] else ""
            media_path = parts[1] if len(parts) > 1 else None

            try:
                await post_tweet_with_media(self.twitter_api, caption, [media_path] if media_path else None)
                await self.bot.answer_callback_query(call.id, "Posted!")
                await self.bot.edit_message_text("✅ Posted successfully!", call.message.chat.id, call.message.message_id)
                # Clean up temp file
                if media_path and os.path.exists(media_path):
                    os.remove(media_path)
            except Exception as e:
                await self.bot.answer_callback_query(call.id, f"Error: {str(e)}")
                await self.bot.edit_message_text(f"❌ Error: {str(e)}", call.message.chat.id, call.message.message_id)

def setup_tweet_handler(bot, twitter_api):
    tweet_handler = TweetHandler(bot, twitter_api)
    bot.register_message_handler(tweet_handler.handle_text, content_types=['text'])
    bot.register_message_handler(tweet_handler.handle_media, content_types=['photo', 'video', 'animation'])
    bot.register_callback_query_handler(tweet_handler.handle_callback, func=lambda call: True)
    bot.register_message_handler(tweet_handler.handle_reply, commands=['reply'])
