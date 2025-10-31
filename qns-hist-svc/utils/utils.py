import os

from dotenv import load_dotenv

load_dotenv()

def get_envvar(var_name: str) -> str:    
    value = os.getenv(var_name)
    if value is None:
        raise ValueError(f"Environment variable {var_name} is not set.")
    return value
