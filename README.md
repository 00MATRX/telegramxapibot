# Telegram X API Bot

A Telegram bot to post tweets to X (formerly Twitter) with support for text, media, replies, and scheduled posts.

## Description

This bot allows a user to manage a Twitter account through Telegram. It provides a simple interface to post text, photos, and videos, reply to tweets, and schedule posts. It also tracks API usage to stay within the monthly limits.

## Features

- **Post Text:** Send a simple text tweet.
- **Post Media:** Upload photos and videos.
- **Reply to Tweets:** Reply to existing tweets by providing the tweet ID.
- **Schedule Posts:** Schedule tweets to be posted at a later time.
- **Usage Tracking:** Monitors the number of posts made in a month to avoid hitting API limits.
- **Confirmation Dialogs:** Asks for confirmation before posting to prevent accidental tweets.

## Architecture

The bot is built with a modular architecture that separates the different components of the application. The main components are:

- **`main.py`:** The entry point of the application. It initializes the Telegram bot and the Twitter API, and sets up the handlers.
- **`telegram/`:** This package contains the Telegram bot implementation.
- **`twitter/`:** This package contains the Twitter API implementation.
- **`handlers/`:** This package contains the handlers for the different Telegram commands and messages.
- **`config.py`:** This file contains the configuration for the bot, such as the API keys and tokens.

## Setup and Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/telegramxapibot.git
   cd telegramxapibot
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the bot:**
   - Create a `.env` file in the root directory of the project.
   - Add the following environment variables to the `.env` file:
     ```
     CONSUMER_KEY="YOUR_CONSUMER_KEY"
     CONSUMER_SECRET="YOUR_CONSUMER_SECRET"
     ACCESS_TOKEN="YOUR_ACCESS_TOKEN"
     ACCESS_TOKEN_SECRET="YOUR_ACCESS_TOKEN_SECRET"
     TELEGRAM_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
     TELEGRAM_USER_ID="YOUR_TELEGRAM_USER_ID"
     ```
   - You can get the Twitter API keys and tokens from the [Twitter Developer Portal](https://developer.twitter.com/).
   - You can get the Telegram bot token from the [BotFather](https://t.me/botfather).
   - Your `TELEGRAM_USER_ID` can be found by messaging the `@userinfobot` on Telegram.

## Usage

1. **Start the bot:**
   ```bash
   python main.py
   ```

2. **Interact with the bot on Telegram:**
   - Use the `/start` command to see the main menu.
   - **Post Text:** Click the "📝 Post Text" button and enter your text.
   - **Post Media:** Send a photo or video to the bot.
   - **Reply to Tweet:** Use the `/reply <tweet_id> <text>` command.
   - **Schedule Post:** Use the `/schedule <minutes> <text>` command.
   - **Check Usage:** Use the `/usage` command to see your current API usage.

## Dependencies

- [tweepy](https://www.tweepy.org/)
- [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI)
- [requests](https://docs.python-requests.org/en/latest/)
- [aiohttp](https://docs.aiohttp.org/en/stable/)
- [python-dotenv](https://github.com/theskumar/python-dotenv)
- [schedule](https://schedule.readthedocs.io/en/stable/)