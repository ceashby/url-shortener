import json
import unittest
from unittest.mock import patch
from url_shortener import app


class TestViews(unittest.TestCase):
    def setUp(self):
        self.test_client = app.test_client()
        self.test_client.testing = True
        self.patcher = patch('url_shortener.views.LinksStore')
        self.links_store = self.patcher.start()

        self.shorten_url = self.links_store.return_value.shorten_url
        self.lengthen_url = self.links_store.return_value.lengthen_url

    def tearDown(self):
        self.patcher.stop()

    def test_shorten_url_returns_201_on_success(self):
        self.shorten_url.return_value = None, '123'
        result = self.test_client.post('/shorten_url', data=json.dumps({'url': 'http://www.example.com'}))
        self.assertEqual(201, result.status_code)

    def test_shorten_url_returns_json_on_success(self):
        short_url = '123'
        self.shorten_url.return_value = None, '123'
        result = self.test_client.post('/shorten_url', data=json.dumps({'url': 'http://www.example.com'}))
        self.assertEqual({'shortened_url': 'http://localhost/' + short_url}, json.loads(result.data))

    def test_shorten_url_returns_400_on_validation_error(self):
        error_message = 'Error occurred'
        self.shorten_url.return_value = error_message, None
        result = self.test_client.post('/shorten_url', data=json.dumps({'url': 'http://www.example.com'}))
        self.assertEqual(400, result.status_code)
        self.assertEqual({'error': error_message}, json.loads(result.data))

    def test_shorten_url_returns_500_on_unexpected_error(self):
        self.shorten_url.side_effect = ValueError
        result = self.test_client.post('/shorten_url', data=json.dumps({'url': 'http://www.example.com'}))
        self.assertEqual(500, result.status_code)
        self.assertEqual({'error': 'Unexpected error: '}, json.loads(result.data))

    def test_shorten_url_returns_error_on_missing_arguments(self):
        result = self.test_client.post('/shorten_url', data=json.dumps({}))
        self.assertEqual(400, result.status_code)
        self.assertEqual({'error': 'Missing argument: "url"'}, json.loads(result.data))

    def test_shorten_url_returns_error_on_no_request_body(self):
        result = self.test_client.post('/shorten_url', data='')
        self.assertEqual(400, result.status_code)
        self.assertEqual({'error': 'Missing argument: "url"'}, json.loads(result.data))

    def test_shorten_url_returns_error_on_invalid_request_body(self):
        result = self.test_client.post('/shorten_url', data='{')
        self.assertEqual(400, result.status_code)
        self.assertEqual({'error': 'Invalid JSON supplied'}, json.loads(result.data))

    def test_redirect_url_redirect_to_retrieved_url(self):
        long_url = "http://www.example.com"
        self.lengthen_url.return_value = long_url
        result = self.test_client.get('/123')
        self.assertEqual(302, result.status_code)
        self.assertEqual(long_url, result.headers['Location'])

    def test_redirect_url_returns_not_found_error_on_not_in_db(self):
        self.lengthen_url.return_value = None
        result = self.test_client.get('/123')
        self.assertEqual(404, result.status_code)
        self.assertEqual({"error": "URL '123' not found"}, json.loads(result.data))