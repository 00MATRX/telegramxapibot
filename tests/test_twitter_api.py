import unittest
from unittest.mock import patch, MagicMock
from twitter.api import TwitterAPI

class TestTwitterAPI(unittest.TestCase):
    @patch('tweepy.OAuth1UserHandler')
    @patch('tweepy.API')
    @patch('tweepy.Client')
    def test_init(self, mock_client, mock_api, mock_auth):
        twitter_api = TwitterAPI()
        self.assertIsNotNone(twitter_api.api)
        self.assertIsNotNone(twitter_api.client)
        mock_auth.assert_called_once()
        mock_api.assert_called_once()
        mock_client.assert_called_once()

if __name__ == '__main__':
    unittest.main()
