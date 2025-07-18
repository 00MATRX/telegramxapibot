from telegram.bot import bot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReactionTypeEmoji
from config import TELEGRAM_USER_ID
from twitter.utils import post_tweet_with_media, download_media
import os
from tempfile import NamedTemporaryFile

@bot.message_handler(content_types=['text'])
async def handle_text(message):
    if message.from_user.id != TELEGRAM_USER_ID:
        return
    text = message.text
    if text not in ["📝 Post Text", "💬 Reply to Tweet", "⏰ Schedule Post", "📊 Check Usage"]:
        await confirm_post(message, text)

async def confirm_post(message, text, media_paths=None, reply_to_id=None):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ Confirm", callback_data=f"confirm:{reply_to_id or ''}:{message.message_id}"))  # Include msg_id for context
    markup.add(InlineKeyboardButton("🗑 Cancel", callback_data="cancel"))
    preview_msg = await bot.reply_to(message, f"Preview: {text}", reply_markup=markup)
    return preview_msg  # Optional for reaction later

@bot.callback_query_handler(func=lambda call: True)
async def handle_callback(call):
    if call.from_user.id != TELEGRAM_USER_ID:
        return
    data = call.data
    if data.startswith("confirm:"):
        parts = data.split(":")
        reply_id = parts[1] if parts[1] else None
        # msg_id = parts[2]  # For future use
        try:
            await post_tweet_with_media(call.message.text.replace("Preview: ", ""), reply_to_id=reply_id)
            await bot.answer_callback_query(call.id, "Posted!")
            await bot.edit_message_text("Posted successfully!", call.message.chat.id, call.message.message_id)
            await bot.set_message_reaction(call.message.chat.id, call.message.message_id, [ReactionTypeEmoji(type="emoji", emoji="👍")])
        except Exception as e:
            await bot.answer_callback_query(call.id, f"Error: {str(e)}")
    elif data == "cancel":
        await bot.answer_callback_query(call.id, "Cancelled.")
        await bot.delete_message(call.message.chat.id, call.message.message_id)
