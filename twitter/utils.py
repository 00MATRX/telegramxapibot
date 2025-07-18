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
