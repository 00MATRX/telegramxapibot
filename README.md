Telegram-X-Poster Bot
This is a Python-based Telegram bot that allows you to post text, photos, videos, and animations to X (formerly Twitter) directly from Telegram. It includes advanced features like scheduling posts, replying to tweets, usage tracking for Free tier compliance, and a modern UI with custom keyboards and inline buttons for an interactive experience. Built for personal use on platforms like Replit.
Features
	•	Post Content to X: Send text, photos, videos, or GIFs from Telegram to X.
	•	Reply to Tweets: Specify a tweet ID to post replies.
	•	Schedule Posts: Queue posts to be sent after a delay (checked every minute).
	•	Usage Tracking: Monitors monthly write caps (e.g., 500 posts/month in Free tier) and warns when approaching limits.
	•	Visual UI:
	◦	Persistent reply keyboard with emoji buttons for quick actions (no typing commands).
	◦	Inline buttons for confirming/cancelling posts.
	◦	Automatic reactions (e.g., 👍) on successful posts.
	◦	Bot commands menu for slash suggestions.
	•	Media Support: Handles photos, videos, and animations with captions.
	•	Security: Restricted to your Telegram user ID; uses environment secrets for credentials.
	•	Compliance: Stays within X Free tier limits (no reads, tracks writes); ethical for personal automation.
Installation
	1	Clone the Repository (or fork on Replit): git clone https://github.com/yourusername/telegram-x-bot.git
	2	cd telegram-x-bot
	3	
	4	Install Dependencies: Run in your terminal or Replit shell: pip install -r requirements.txt
	5	 Requirements (pinned versions for stability):
	◦	tweepy==4.16.0
	◦	pyTelegramBotAPI==4.27.0
	◦	requests==2.32.4
	◦	aiohttp==3.12.14
	◦	python-dotenv==1.1.1
	◦	schedule==1.2.2
Setup
	1	X Developer Credentials:
	◦	Create an app at developer.x.com.
	◦	Get API Key (Consumer Key), API Secret, Access Token, Access Secret.
	◦	In Replit, add as Secrets: CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET.
	2	Telegram Bot Credentials:
	◦	Create a bot via @BotFather to get TELEGRAM_TOKEN.
	◦	Get your user ID via @userinfobot.
	◦	Add as Secrets: TELEGRAM_TOKEN, TELEGRAM_USER_ID.
	3	Run the Bot:
	◦	On Replit: Click “Run” (enable “Always On” for 24/7 if needed).
	◦	Locally: python main.py.
	◦	Message your bot with /start to see the menu.
Usage
	1	Start the Bot: Send /start to get the reply keyboard menu.
	2	Post Text: Tap “📝 Post Text” > Enter text > Confirm via inline button.
	3	Post Media: Tap “🎥 Post Video” or similar > Send file with caption > Confirm.
	4	Reply: Tap “💬 Reply to Tweet” > Enter “ID text” > Confirm.
	5	Schedule: Tap “⏰ Schedule Post” > Enter “mins text”.
	6	Check Usage: Tap “📊 Check Usage” for monthly post count.
	7	Feedback: Successful posts get a 👍 reaction; errors notify you.
Monitor X Developer Portal for usage to stay under Free tier caps.
Code Structure
	•	config.py: Loads secrets and constants (e.g., write cap).
	•	utils.py: Core functions for posting, downloading, tracking usage.
	•	scheduler.py: Handles scheduled post queue.
	•	main.py: Bot handlers, keyboards, callbacks, async polling.
	•	usage.json: Persistent file for tracking (git ignored).
Contributing
Fork the repo, make changes, and submit a PR with a commit message and description. Test on Replit before submitting.
License
MIT License - Free to use/modify for personal projects. See LICENSE file for details.
