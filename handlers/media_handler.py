from telegram.bot import bot
from config import TELEGRAM_USER_ID
from twitter.utils import download_media
from handlers.tweet_handler import confirm_post
import os
from tempfile import NamedTemporaryFile

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

@bot.message_handler(func=lambda message: message.text in ["🎥 Post Video", "🖼 Post Photo"])
async def handle_media_button(message):
    if message.from_user.id != TELEGRAM_USER_ID:
        return
    await bot.reply_to(message, "Send the media to post.")
