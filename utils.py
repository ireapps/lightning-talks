import settings

from pymongo import MongoClient


def connect(collection):
    client = MongoClient()
    d = client[settings.MONGO_DATABASE]
    return d[collection]
