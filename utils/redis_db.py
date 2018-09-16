import redis


def get_redis_connection(host, port, db):
    connection_pool = redis.ConnectionPool(host=host, port=port, db=db)
    return redis.Redis(connection_pool=connection_pool)
