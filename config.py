import os
from dotenv import load_dotenv

load_dotenv()  # Loads from .env or Replit secrets

CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_USER_ID_STR = os.getenv("TELEGRAM_USER_ID")
if TELEGRAM_USER_ID_STR is None:
    raise ValueError("TELEGRAM_USER_ID environment variable not set")
TELEGRAM_USER_ID = int(TELEGRAM_USER_ID_STR)

MONTHLY_WRITE_CAP = 500
