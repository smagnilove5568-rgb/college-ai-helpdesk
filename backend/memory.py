import redis
import json
import os

# connect to redis
redis_url = os.getenv("REDIS_URL")

redis_client = redis.from_url(
    redis_url,
    decode_responses=True
)

def get_history(session_id):
    data = redis_client.get(session_id)

    if data:
        return json.loads(data)

    return []

def save_history(session_id, history):
    redis_client.set(session_id, json.dumps(history))