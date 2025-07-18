import aiohttp
import logging
import time
import json
import os
import asyncio
from functools import wraps
from config import MONTHLY_WRITE_CAP, USAGE_FILE
from twitter.api import client, api
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
                # The `media_upload` method is on the `API` object, not the `Client` object.
                # It's also a synchronous method, so we need to run it in a separate thread.
                loop = asyncio.get_event_loop()
                media = await loop.run_in_executor(None, lambda: api.media_upload(filename=path))
                media_ids.append(media.media_id_string)
                logging.info(f"Media uploaded: {media.media_id}")
            except tweepy.TweepyException as e:
                logging.error(f"Upload failed: {e}")
                raise

    try:
        response = client.create_tweet(text=text, media_ids=media_ids if media_ids else None, in_reply_to_tweet_id=reply_to_id)
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
