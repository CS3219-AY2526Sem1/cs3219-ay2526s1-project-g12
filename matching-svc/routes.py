from fastapi import FastAPI
from service.redis_service import connect_to_redis

app = FastAPI()

redis_connection = connect_to_redis()

@app.get("/")
async def root():
    x = redis_connection.ping()
    return {"status": x}




