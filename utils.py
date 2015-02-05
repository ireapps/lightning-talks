import settings

from pymongo import MongoClient


def connect(collection, db=None):
    if not db:
        db = settings.MONGO_DATABASE
    client = MongoClient()
    d = client[db]
    return d[collection]
