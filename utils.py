from pymongo import MongoClient

import app
import settings


def connect(collection):
    client = MongoClient()
    d = client[settings.MONGO_DATABASE]
    return d[collection]


def bake():
    from flask import g

    for route in ['index']:
        with (app.app.test_request_context(path="/%s.html" % route)):
            view = globals()['app'].__dict__[route]
            file_path = "www/%s.html" % route
            with open(file_path, "w") as writefile:
                writefile.write(view())
            print "wrote %s" % file_path