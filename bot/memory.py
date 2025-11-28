import os
import redis

r = redis.Redis.from_url(os.getenv("UPSTASH_REDIS_URL"), password=os.getenv("UPSTASH_REDIS_TOKEN"))

def save_context(user_id, msg):
    key = f"ctx:{user_id}"
    prev = r.get(key)
    prev = prev.decode() if prev else ""
    new = (prev + " | " + msg)[-600:]  # máximo 600 chars
    r.set(key, new)

def get_context(user_id):
    val = r.get(f"ctx:{user_id}")
    return val.decode() if val else ""
