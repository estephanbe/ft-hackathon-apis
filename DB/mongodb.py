# app/DB/mongodb.py
from config import settings
from mongoengine import connect, disconnect


async def get_mongo_db():
    try:
        connect(settings.MONGO_INITDB_DATABASE, host=settings.MONGODB_URL)
    except Exception as e:
        print(e)


async def close_mongo_db():
    disconnect()


def load_mongo_db():
    try:
        connect(settings.MONGO_INITDB_DATABASE, host=settings.MONGODB_URL)
    except Exception as e:
        print(e)
    finally:
        disconnect()
