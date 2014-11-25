import settings

from pymongo import MongoClient


def connect(collection):
    client = MongoClient()
    db = client[settings.MONGO_DATABASE]
    return db[collection]
