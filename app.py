#!/usr/bin/env python
import argparse
import json
import os

from flask import Flask, make_response, render_template
from pymongo import MongoClient

from models import User

app = Flask(__name__)


DEPLOYMENT_TARGET = os.environ.get('DEPLOYMENT_TARGET', 'development')
MONGO_DATABASE = 'lightningtalk-%s' % DEPLOYMENT_TARGET

DEBUG = True
if DEPLOYMENT_TARGET in ['staging', 'production']:
    DEBUG = False


@app.route('/api/<string:collection>/')
def api_collection(collection=None, methods=['GET']):
        client = MongoClient()
        db = client[MONGO_DATABASE]
        collection = db[collection]
        return json.dumps(list(collection.find()))


@app.route('/api/user/login/')
def login(methods=['GET']):

    from flask import request
    email = request.args.get('email', None)
    password = request.args.get('password', None)

    client = MongoClient()
    db = client[MONGO_DATABASE]
    collection = db['user']

    error = json.dumps({"success": False, "text": "Username or password is incorrect."})

    try:
        user_dict = dict(collection.find_one({ "email": email }))
        u = User(**user_dict)

        if u.auth_user(password):
            return json.dumps({"success": True, "_id": u._id})

        return error

    except:
        return error


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port')
    args = parser.parse_args()
    server_port = 8000

    if args.port:
        server_port = int(args.port)

    app.run(host='0.0.0.0', port=server_port, debug=DEBUG)