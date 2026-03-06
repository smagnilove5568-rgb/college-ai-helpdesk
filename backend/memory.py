import redis
import json
import os

# connect to redis
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)


def get_history(session_id):
    data = redis_client.get(session_id)

    if data:
        return json.loads(data)

    return []


def save_history(session_id, history):
    redis_client.set(session_id, json.dumps(history))