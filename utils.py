import tweepy
import aiohttp
import logging
import time
import json
import os
from functools import wraps
from config import MONTHLY_WRITE_CAP, USAGE_FILE

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
async def post_tweet_with_media(client, api, text, media_paths=None, reply_to_id=None):
    media_ids = []
    if media_paths:
        for path in media_paths:
            try:
                media = api.media_upload(filename=path)
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

def track_usage(reset=False):
    if reset or not os.path.exists(USAGE_FILE):
        data = {"writes": 0, "month": time.strftime("%Y-%m")}
    else:
        try:
            with open(USAGE_FILE, "r") as f:
                data = json.load(f)
        except:
            data = {"writes": 0, "month": time.strftime("%Y-%m")}

    current_month = time.strftime("%Y-%m")
    if data["month"] != current_month:
        data = {"writes": 0, "month": current_month}

    if not reset:
        data["writes"] += 1
        if data["writes"] > MONTHLY_WRITE_CAP * 0.9:
            logging.warning(f"Near cap: {data['writes']}/{MONTHLY_WRITE_CAP}")

    with open(USAGE_FILE, "w") as f:
        json.dump(data, f)

    return data["writes"]

async def download_media(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=30) as resp:
            resp.raise_for_status()
            return await resp.read()

# Init tracking
track_usage()
