#!/usr/bin/env python
import argparse
import json
import os

from flask import Flask, make_response, render_template
from pymongo import MongoClient

import models
import settings
import utils

app = Flask(__name__)

@app.route('/api/session/')
def api_session(collection=None, methods=['GET']):
    from flask import request
    _id = request.args.get('_id', None)
    if not _id:
        return json.dumps(list(utils.connect('session').find({})))

    session = dict(utils.connect('session').find_one({"_id": _id}))

    return json.dumps(session)

@app.route('/api/user/')
def api_user(methods=['GET']):
    from flask import request
    _id = request.args.get('_id', None)
    if not _id:
        return json.dumps(list(utils.connect('user').find({})))

    user = dict(utils.connect('user').find_one({"_id": _id}))
    for x in ['login_hash', 'name', 'updated', 'created', 'password', 'fingerprint']:
        del user[x]

    return json.dumps(user)


@app.route('/api/user/action/')
def action(methods=['GET']):
    from flask import request
    email = request.args.get('email', None)
    password = request.args.get('password', None)

    not_found = json.dumps({"success": False, "text": "Username or password is incorrect."})

    user = utils.connect('user').find_one({ "email": email })

    if not user:
        name = request.args.get('name', None)
        if not name:
            return not_found

        u = models.User(email=email, name=name, password=password)
        u.save()
        return json.dumps({"success": True, "_id": u._id, "action": "register"})

    else:
        user_dict = dict(user)
        u = models.User(**user_dict)

        if u.auth_user(password):
            return json.dumps({"success": True, "_id": u._id, "action": "login"})

    return not_found


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port')
    args = parser.parse_args()
    server_port = 8000

    if args.port:
        server_port = int(args.port)

    app.run(host='0.0.0.0', port=server_port, debug=settings.DEBUG)