import validators
from url_shortener.stores.id_counter_store import IDCounterStore
from url_shortener.stores.ids_by_long_url_store import IDsByLongURLStore
from url_shortener.stores.long_urls_by_id_store import LongURLsByIDStore
from utils import base_62_encoding
import math


class LinksStore:
    def __init__(self, redis_db, number_of_counters, max_id, max_url_length):
        self.id_counter = IDCounterStore(
            redis_db,
            number_of_counters=number_of_counters,
            max_id=max_id
        )
        self.max_digits = math.ceil(math.log(max_id, 62))
        self.ids_by_long_url = IDsByLongURLStore(redis_db)
        self.long_urls_by_id = LongURLsByIDStore(redis_db)
        self.max_url_length = max_url_length

    def shorten_url(self, long_url):
        is_valid = validators.url(long_url)
        if not is_valid:
            return 'Invalid URL supplied', None

        if len(long_url) > self.max_url_length:
            return 'URL is too long', None

        link_id = self.get_or_create_link(long_url)
        return None, self.short_url_from_id(link_id)

    def lengthen_url(self, short_url):
        link_id = self.id_from_short_url(short_url)
        return self.long_urls_by_id.get(link_id)

    def get_or_create_link(self, long_url):
        existing_id = self.ids_by_long_url.get(long_url)
        if existing_id:
            return existing_id

        link_id = self.id_counter.get_new_id()
        self.long_urls_by_id.set(link_id, long_url)
        self.ids_by_long_url.set(long_url, link_id)
        return link_id

    def short_url_from_id(self, id):
        return base_62_encoding.encode(id, self.max_digits)

    def id_from_short_url(self, short_url_path):
        return base_62_encoding.decode(short_url_path)


