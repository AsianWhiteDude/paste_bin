import redis
from tasks import create_hash_keys


def get_key():

    create_hash_keys.delay()

    redis_client = redis.StrictRedis(host='redis', port=6379, decode_responses=True)
    hash_key = redis_client.rpop('valid_hashes')
    redis_client.close()

    return hash_key