import unittest
from unittest.mock import patch, MagicMock
from telegram.bot import TelegramBot

class TestTelegramBot(unittest.TestCase):
    @patch('telegram.bot.AsyncTeleBot')
    def test_init(self, mock_async_telebot):
        # Create a mock instance of AsyncTeleBot
        mock_bot_instance = MagicMock()
        mock_async_telebot.return_value = mock_bot_instance

        # Initialize TelegramBot with a dummy token
        telegram_bot = TelegramBot('123456:ABC-DEF1234567890')

        # Assert that AsyncTeleBot was called with the token
        mock_async_telebot.assert_called_once_with('123456:ABC-DEF1234567890')

        # Assert that the bot attribute is set to the mock instance
        self.assertEqual(telegram_bot.bot, mock_bot_instance)

if __name__ == '__main__':
    unittest.main()
