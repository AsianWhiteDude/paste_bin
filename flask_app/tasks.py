from random import choice

import redis
from celery import Celery

symbols = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

celery = Celery(
    'tasks',
    backend='redis://redis:6379/0',
    broker='redis://redis:6379/0',
)

@celery.task()
def create_hash_keys():
    redis_client = redis.StrictRedis(host='redis', port=6379, decode_responses=True)
    if redis_client.llen('valid_hashes') >= 50:
        redis_client.close()
        return 'More than 50 values'

    for _ in range(100):
        string = ''
        while True:
            while len(string) < 9:
                string += choice(symbols)
            if redis_client.get(string):
                string = ''
            else:
                break
        redis_client.rpush('valid_hashes', string)

    redis_client.close()

    return 'TASK IS DONE'
