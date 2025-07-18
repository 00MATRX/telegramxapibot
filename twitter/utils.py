import aiohttp
import logging
import time
import json
import os
import asyncio
from functools import wraps
from config import MONTHLY_WRITE_CAP, USAGE_FILE
from twitter.api import twitter_api
import tweepy

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def retry_on_rate_limit(max_retries=3, backoff_factor=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except (tweepy.TooManyRequests, tweepy.TweepyException) as e:
                    if isinstance(e, tweepy.TooManyRequests):
                        wait_time = backoff_factor ** retries
                        logging.warning(f"Rate limit hit: {e}. Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        retries += 1
                    else:
                        logging.error(f"API error: {e}")
                        raise
            raise Exception("Max retries exceeded.")
        return wrapper
    return decorator

@retry_on_rate_limit()
async def post_tweet_with_media(text, media_paths=None, reply_to_id=None):
    media_ids = []
    if media_paths:
        for path in media_paths:
            try:
                loop = asyncio.get_event_loop()
                media = await loop.run_in_executor(None, lambda: twitter_api.api.media_upload(filename=path))
                media_ids.append(media.media_id_string)
                logging.info(f"Media uploaded: {media.media_id}")
            except tweepy.TweepyException as e:
                logging.error(f"Upload failed: {e}")
                raise

    try:
        response = twitter_api.client.create_tweet(text=text, media_ids=media_ids if media_ids else None, in_reply_to_tweet_id=reply_to_id)
        logging.info(f"Posted: https://x.com/i/status/{response.data['id']}")
        track_usage()
        return response
    except tweepy.TweepyException as e:
        logging.error(f"Post failed: {e}")
        raise

import sqlite3

def init_db():
    conn = sqlite3.connect('usage.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS usage (
            month TEXT PRIMARY KEY,
            writes INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def track_usage(reset=False):
    init_db()
    conn = sqlite3.connect('usage.db')
    c = conn.cursor()

    current_month = time.strftime("%Y-%m")

    c.execute("SELECT writes FROM usage WHERE month = ?", (current_month,))
    result = c.fetchone()

    if result is None:
        c.execute("INSERT INTO usage (month, writes) VALUES (?, ?)", (current_month, 0))
        writes = 0
    else:
        writes = result[0]

    if not reset:
        writes += 1
        if writes > MONTHLY_WRITE_CAP * 0.9:
            logging.warning(f"Near cap: {writes}/{MONTHLY_WRITE_CAP}")

    c.execute("UPDATE usage SET writes = ? WHERE month = ?", (writes, current_month))
    conn.commit()
    conn.close()

    return writes

async def download_media(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=30) as resp:
            resp.raise_for_status()
            return await resp.read()

# Init tracking
track_usage()
import json
import os
import aiohttp
from datetime import datetime
from config import USAGE_FILE, MONTHLY_WRITE_CAP

async def post_tweet_with_media(twitter_api, text, media_paths=None, reply_to_id=None):
    """Post a tweet with optional media and reply functionality"""
    try:
        media_ids = []
        if media_paths:
            for media_path in media_paths:
                if os.path.exists(media_path):
                    media = twitter_api.api.media_upload(media_path)
                    media_ids.append(media.media_id)
        
        # Post the tweet
        if reply_to_id:
            tweet = twitter_api.client.create_tweet(
                text=text,
                media_ids=media_ids if media_ids else None,
                in_reply_to_tweet_id=reply_to_id
            )
        else:
            tweet = twitter_api.client.create_tweet(
                text=text,
                media_ids=media_ids if media_ids else None
            )
        
        # Track usage
        increment_usage()
        return tweet
    except Exception as e:
        raise Exception(f"Twitter API error: {str(e)}")

async def download_media(bot, file_id, media_type):
    """Download media from Telegram and save to temp file"""
    try:
        file_info = await bot.get_file(file_id)
        file_path = file_info.file_path
        
        # Get file extension
        ext = os.path.splitext(file_path)[1] or '.jpg'
        
        # Create temp file
        temp_path = f"/tmp/{file_id}{ext}"
        
        # Download file
        async with aiohttp.ClientSession() as session:
            url = f"https://api.telegram.org/file/bot{bot.token}/{file_path}"
            async with session.get(url) as response:
                if response.status == 200:
                    with open(temp_path, 'wb') as f:
                        f.write(await response.read())
                    return temp_path
        
        raise Exception("Failed to download media")
    except Exception as e:
        raise Exception(f"Media download error: {str(e)}")

def track_usage():
    """Get current usage count"""
    if not os.path.exists(USAGE_FILE):
        return 0
    
    try:
        with open(USAGE_FILE, 'r') as f:
            data = json.load(f)
            current_month = datetime.now().strftime("%Y-%m")
            return data.get(current_month, 0)
    except:
        return 0

def increment_usage():
    """Increment usage count for current month"""
    current_month = datetime.now().strftime("%Y-%m")
    data = {}
    
    if os.path.exists(USAGE_FILE):
        try:
            with open(USAGE_FILE, 'r') as f:
                data = json.load(f)
        except:
            pass
    
    data[current_month] = data.get(current_month, 0) + 1
    
    with open(USAGE_FILE, 'w') as f:
        json.dump(data, f)
    
    return data[current_month]
