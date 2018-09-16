

class LongURLsByIDStore:
    def __init__(self, redis_db):
        self.redis_db = redis_db

    def get(self, id):
        value = self.redis_db.get(self.make_key(id))
        if value:
            return value.decode('UTF-8')

    def set(self, id, long_url):
        self.redis_db.set(self.make_key(id), long_url)

    @staticmethod
    def make_key(id):
        return 'long_urls_by_id:{}'.format(id)
