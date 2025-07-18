import tweepy
import logging
import time
from functools import wraps

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def retry_on_rate_limit(max_retries=3, backoff_factor=2):
    """Decorator for exponential backoff on rate limits (429)."""
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
                        logging.warning(f"Rate limit hit: {e}. Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        retries += 1
                    else:
                        logging.error(f"API error: {e}")
                        raise
            raise Exception("Max retries exceeded for rate limit.")
        return wrapper
    return decorator

@retry_on_rate_limit()
def post_tweet_with_media(client, api, text, video_path=None):
    """Post a tweet with optional video media (via v1.1 upload for Free tier)."""
    media_ids = None
    if video_path:
        try:
            # Upload media (videos up to 512MB/15min; Tweepy handles chunking)
            media = api.media_upload(filename=video_path)
            media_ids = [media.media_id_string]
            logging.info(f"Media uploaded: {media.media_id}")
        except tweepy.TweepyException as e:
            logging.error(f"Media upload failed: {e}")
            raise

    try:
        response = client.create_tweet(text=text, media_ids=media_ids)
        logging.info(f"Tweet posted: https://x.com/i/status/{response.data['id']}")
        return response
    except tweepy.TweepyException as e:
        logging.error(f"Failed to post tweet: {e}")
        raise
