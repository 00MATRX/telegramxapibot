from telebot.async_telebot import AsyncTeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, BotCommand, ReactionTypeEmoji
import os
from tempfile import NamedTemporaryFile
from config import *
from utils import post_tweet_with_media, download_media, track_usage
import tweepy
import logging
import asyncio
from scheduler import run_scheduler, queued_posts

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)
client = tweepy.Client(consumer_key=CONSUMER_KEY, consumer_secret=CONSUMER_SECRET,
                       access_token=ACCESS_TOKEN, access_token_secret=ACCESS_TOKEN_SECRET)

bot = AsyncTeleBot(TELEGRAM_TOKEN)

async def set_commands():
    commands = [
        BotCommand("start", "Start the bot with menu"),
        BotCommand("reply", "Reply to a tweet"),
        BotCommand("schedule", "Schedule a post"),
        BotCommand("usage", "Check monthly usage")
    ]
    await bot.set_my_commands(commands)

@bot.message_handler(commands=['start'])
async def send_welcome(message):
    if message.from_user.id != TELEGRAM_USER_ID:
        await bot.reply_to(message, "Unauthorized.")
        return
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    markup.add(KeyboardButton("📝 Post Text"))
    markup.add(KeyboardButton("🎥 Post Video"), KeyboardButton("🖼 Post Photo"))
    markup.add(KeyboardButton("💬 Reply to Tweet"), KeyboardButton("⏰ Schedule Post"))
    markup.add(KeyboardButton("📊 Check Usage"))
    await bot.reply_to(message, "Advanced bot ready! Tap buttons below.", reply_markup=markup)

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

@bot.message_handler(commands=['schedule'])
async def handle_schedule(message):
    if message.from_user.id != TELEGRAM_USER_ID:
        return
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await bot.reply_to(message, "Usage: /schedule <mins> <text>")
        return
    mins = int(parts[1])
    text = parts[2]
    queued_posts.append((text, None, None, bot))
    await bot.reply_to(message, f"Scheduled in ~{mins} mins (checked minutely).")
    await asyncio.sleep(mins * 60)

@bot.message_handler(commands=['usage'])
async def handle_usage(message):
    if message.from_user.id != TELEGRAM_USER_ID:
        return
    usage = track_usage()
    await bot.reply_to(message, f"Usage: {usage}/{MONTHLY_WRITE_CAP} posts this month.")

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
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_info.file_path}"
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
            await post_tweet_with_media(client, api, call.message.text.replace("Preview: ", ""), reply_to_id=reply_id)
            await bot.answer_callback_query(call.id, "Posted!")
            await bot.edit_message_text("Posted successfully!", call.message.chat.id, call.message.message_id)
            await bot.set_message_reaction(call.message.chat.id, call.message.message_id, [ReactionTypeEmoji(type="emoji", emoji="👍")])
        except Exception as e:
            await bot.answer_callback_query(call.id, f"Error: {str(e)}")
    elif data == "cancel":
        await bot.answer_callback_query(call.id, "Cancelled.")
        await bot.delete_message(call.message.chat.id, call.message.message_id)

async def main():
    await set_commands()
    logging.info("Starting async polling...")
    asyncio.create_task(asyncio.to_thread(run_scheduler, client, api, bot))
    await bot.infinity_polling()

if __name__ == "__main__":
    track_usage()
    asyncio.run(main())
