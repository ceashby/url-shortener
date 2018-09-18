

class IDsByLongURLStore:
    def __init__(self, redis_db):
        self.redis_db = redis_db

    def get(self, long_url):
        value = self.redis_db.get(self.make_key(long_url))
        if value:
            return int(value)

    def set(self, long_url, id):
        self.redis_db.set(self.make_key(long_url), id)

    @staticmethod
    def make_key(long_url):
        return 'ids_by_long_url:{}'.format(long_url)