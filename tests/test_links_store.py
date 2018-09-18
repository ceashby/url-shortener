import unittest
from unittest.mock import patch
from url_shortener.stores.links_store import LinksStore
import fakeredis


class LinksStoreTests(unittest.TestCase):
    def setUp(self):
        self.patcher = patch('url_shortener.stores.links_store.IDCounterStore')
        self.mock_counter = self.patcher.start()

        def count():
            self.count += 1
            return self.count

        self.count = 0
        self.mock_counter.return_value.get_new_id = count

        self.redis_db = fakeredis.FakeStrictRedis()
        self.links_store = LinksStore(
            redis_db=self.redis_db,
            number_of_counters=992,
            max_id=62 ** 5,
            max_url_length=1000
        )

    def tearDown(self):
        self.patcher.stop()
        self.redis_db.flushall()

    def test_returns_error_if_no_url(self):
        error_message, _ = self.links_store.shorten_url('')
        self.assertEqual(error_message, 'Invalid URL supplied')

    def test_returns_error_if_invalid_url(self):
        error_message, _ = self.links_store.shorten_url('not a url')
        self.assertEqual(error_message, 'Invalid URL supplied')

    def test_returns_error_if_url_too_long(self):
        error_message, _ = self.links_store.shorten_url('a' * 2000)
        self.assertEqual(error_message, 'Invalid URL supplied')

    def test_creates_shortened_url(self):
        long_url = "http://example.com"
        error_message, short_url = self.links_store.shorten_url(long_url)
        self.assertFalse(error_message)
        self.assertEqual('00001', short_url)

    def test_can_retrieve_shortened_url(self):
        long_url = "http://example.com"
        error_message, short_url = self.links_store.shorten_url(long_url)

        actual_long_url = self.links_store.lengthen_url(short_url)
        self.assertEqual(long_url, actual_long_url)

    def test_no_new_url_if_already_exists(self):
        long_url = "http://example.com"
        error_message, short_url1 = self.links_store.shorten_url(long_url)
        error_message, short_url2 = self.links_store.shorten_url(long_url)
        self.assertEqual(short_url1, short_url2)

    def test_returns_none_if_short_url_not_present(self):
        long_url = self.links_store.lengthen_url('123')
        self.assertFalse(long_url)

    def test_all_keys_stored_correctly(self):
        url1 = 'http://one.com'
        url2 = 'http://two.com'
        self.links_store.shorten_url(url1)
        self.links_store.shorten_url(url2)
        self.assertEqual({
            b'long_urls_by_id:1': url1.encode(),
            b'long_urls_by_id:2': url2.encode(),
            b'ids_by_long_url:' + url1.encode(): b'1',
            b'ids_by_long_url:' + url2.encode(): b'2',
        }, dict(self.redis_db))