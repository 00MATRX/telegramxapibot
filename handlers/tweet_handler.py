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
    if text == "📝 Post Text":
        await bot.reply_to(message, "Enter text to post:")
        return
    elif text == "💬 Reply to Tweet":
        await bot.reply_to(message, "Enter tweet ID and text (ID text):")
        return
    elif text == "⏰ Schedule Post":
        await bot.reply_to(message, "Enter mins and text (mins text):")
        return
    elif text == "📊 Check Usage":
        from handlers.usage_handler import handle_usage
        await handle_usage(message)
        return
    else:
        await confirm_post(message, text)

@bot.message_handler(content_types=['photo', 'video', 'animation'])
async def handle_media(message):
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

        file_info = await bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"
        content = await download_media(file_url)

        with NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
            temp_file.write(content)
            media_paths.append(temp_file.name)

        await confirm_post(message, text, media_paths=media_paths)
    except Exception as e:
        await bot.reply_to(message, f"Error: {str(e)}")
        await bot.send_message(TELEGRAM_USER_ID, f"Alert: {str(e)}")
    finally:
        for path in media_paths:
            if os.path.exists(path):
                os.unlink(path)

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

@bot.message_handler(commands=['reply'])
async def handle_reply(message):
    if message.from_user.id != TELEGRAM_USER_ID:
        return
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await bot.reply_to(message, "Usage: /reply <tweet_id> <text>")
        return
    reply_id, text = parts[1], parts[2]
    await confirm_post(message, text, reply_to_id=reply_id)
