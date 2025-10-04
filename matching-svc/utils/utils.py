import os
from dotenv import load_dotenv

def get_envvar(var_name: str) -> str:
    load_dotenv()
    value = os.getenv(var_name)
    if value is None:
        raise ValueError(f"Environment variable {var_name} is not set.")
    return value

def format_redis_queue_key(difficulty:str, category:str) -> str:
    """
    Format the difficulty and category into a key to be used in redis.
    """
    key = f"queue:{difficulty}:{category}"
    return key