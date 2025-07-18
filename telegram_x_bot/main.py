import telebot
import requests
import os
from tempfile import NamedTemporaryFile
from config import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, TELEGRAM_TOKEN, ALLOWED_USER_ID
from utils import post_tweet_with_media
import tweepy
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    # Initialize Tweepy (OAuth 1.0a User Context for Free tier posting)
    auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)  # v1.1 for media upload
    client = tweepy.Client(consumer_key=CONSUMER_KEY, consumer_secret=CONSUMER_SECRET,
                           access_token=ACCESS_TOKEN, access_token_secret=ACCESS_TOKEN_SECRET)  # v2 for tweet post

    # Initialize Telegram bot
    bot = telebot.TeleBot(TELEGRAM_TOKEN)

    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        if message.from_user.id != ALLOWED_USER_ID:
            bot.reply_to(message, "Unauthorized user.")
            return
        bot.reply_to(message, "Send me text to tweet, or a video with caption!")

    @bot.message_handler(content_types=['text'])
    def handle_text(message):
        if message.from_user.id != ALLOWED_USER_ID:
            bot.reply_to(message, "Unauthorized user.")
            return
        text = message.text
        try:
            post_tweet_with_media(client, api, text)
            bot.reply_to(message, "Tweet posted!")
        except Exception as e:
            bot.reply_to(message, f"Error posting tweet: {str(e)}")

    @bot.message_handler(content_types=['video'])
    def handle_video(message):
        if message.from_user.id != ALLOWED_USER_ID:
            bot.reply_to(message, "Unauthorized user.")
            return
        text = message.caption or "Video tweet via Telegram bot"
        try:
            # Download video from Telegram
            file_info = bot.get_file(message.video.file_id)
            file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_info.file_path}"
            response = requests.get(file_url)
            response.raise_for_status()

            # Save to temp file
            with NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
                temp_file.write(response.content)
                video_path = temp_file.name

            try:
                post_tweet_with_media(client, api, text, video_path)
                bot.reply_to(message, "Tweet with video posted!")
            finally:
                os.unlink(video_path)  # Clean up
        except Exception as e:
            bot.reply_to(message, f"Error: {str(e)}")

    # Start polling
    logging.info("Starting Telegram bot polling...")
    bot.polling(none_stop=True)

if __name__ == "__main__":
    main()
