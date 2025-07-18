from telegram.bot import bot
from twitter.api import twitter_api

class BaseHandler:
    def __init__(self, bot, twitter_api):
        self.bot = bot
        self.twitter_api = twitter_api
