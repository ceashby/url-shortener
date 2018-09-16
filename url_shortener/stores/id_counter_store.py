from random import randint


class IDCounterStore:
    def __init__(self, redis_db, number_of_counters, max_id):
        self.redis_db = redis_db
        self.number_of_counters = number_of_counters
        self.max_id = max_id
        self.max_value_per_counter = max_id // number_of_counters

    def get_new_id(self):
        counter_id = self.random_counter_id()
        counter_value = self.redis_db.incr(self.make_key(counter_id))

        if counter_value > self.max_value_per_counter:
            raise OverflowError('No more ids available for counter {}'.format(counter_id))

        return counter_value + counter_id * self.max_value_per_counter

    @staticmethod
    def make_key(counter_id):
        return 'counter:{}'.format(counter_id)

    def random_counter_id(self):
        return randint(0, self.number_of_counters - 1)