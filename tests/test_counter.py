import unittest
from unittest.mock import patch
import fakeredis
from url_shortener.stores.id_counter_store import IDCounterStore


class CounterTests(unittest.TestCase):
    def setUp(self):
        self.patcher = patch('url_shortener.stores.id_counter_store.randint')
        self.randint = self.patcher.start()
        self.randint.return_value = 0
        self.redis_db = fakeredis.FakeStrictRedis()

        self.id_counter = IDCounterStore(
            redis_db=self.redis_db,
            number_of_counters=5,
            max_id=25
        )

    def tearDown(self):
        self.redis_db.flushall()

    def test_get_ids(self):
        self.randint.return_value = 0
        new_id = self.id_counter.get_new_id()
        self.assertEqual(new_id, 1)
        new_id = self.id_counter.get_new_id()
        self.assertEqual(new_id, 2)
        self.randint.return_value = 1
        new_id = self.id_counter.get_new_id()
        self.assertEqual(new_id, 6)

    def test_counter_saves_to_redis(self):
        self.randint.return_value = 0
        self.assertFalse(self.redis_db.exists('counter:{}'.format(0)))
        self.id_counter.get_new_id()
        self.assertEqual(self.redis_db.get('counter:{}'.format(0)), b'1')
        self.id_counter.get_new_id()
        self.assertEqual(self.redis_db.get('counter:{}'.format(0)), b'2')

    def test_error_on_counter_overflow(self):
        for i in range(5):
            self.id_counter.get_new_id()

        with self.assertRaises(OverflowError):
            self.id_counter.get_new_id()
