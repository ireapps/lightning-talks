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

@app.route('/')
def session_list():
    sessions = utils.connect('session').find({})
    if sessions:
        sessions = sorted(sessions, key=lambda x: x['votes'], reverse=True)
    else:
        sessions = []
    return render_template('session_list.html', sessions=sessions)

@app.route('/api/vote/action/')
def vote_action(methods=['GET']):
    from flask import request
    session = request.args.get('session')
    user = request.args.get('user')

    error = json.dumps({"success": False, "text": "Please send a session ID and a user ID."})

    if not session or not user:
        return error

    u = utils.connect('user').find_one({"_id": user})

    if not u:
        return error

    s = utils.connect('session').find_one({"_id": session})

    if not s:
        return error

    v = utils.connect('vote').find_one({"user": user, "session": session})

    if not v:
        models.Vote(user=u['_id'], session=s['_id']).save()
        return json.dumps({"success": True, "action": "vote"})

    return json.dumps({"success": False, "text": "You've already voted here!"})

@app.route('/api/vote/')
def api_vote(methods=['GET']):
    from flask import request
    _id = request.args.get('_id', None)
    if not _id:
        return json.dumps(list(utils.connect('vote').find({})))

    vote = dict(utils.connect('vote').find_one({"_id": _id}))

    return json.dumps(vote)

@app.route('/api/session/')
def api_session(methods=['GET']):
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
    for x in ['login_hash', 'updated', 'created', 'password', 'fingerprint']:
        del user[x]

    return json.dumps(user)


@app.route('/api/user/action/')
def user_action(methods=['GET']):
    from flask import request
    email = request.args.get('email', None)
    password = request.args.get('password', None)

    not_found = json.dumps({"success": False, "text": "Username or password is incorrect."})

    user = utils.connect('user').find_one({ "email": email })

    if not user:
        name = request.args.get('name', None)
        fingerprint = request.args.get('fingerprint', None)
        if not name or not fingerprint:
            return not_found

        u = models.User(email=email, name=name, password=password, fingerprint=fingerprint)
        u.save()
        return json.dumps({"success": True, "_id": u._id, "name": u.name, "votes": "|".join(u.sessions_voted_for), "action": "register"})

    else:
        user_dict = dict(user)
        u = models.User(**user_dict)

        if u.auth_user(password):
            return json.dumps({"success": True, "_id": u._id, "name": u.name, "votes": "|".join(u.sessions_voted_for), "action": "login"})

    return not_found


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port')
    args = parser.parse_args()
    server_port = 8000

    if args.port:
        server_port = int(args.port)

    app.run(host='0.0.0.0', port=server_port, debug=settings.DEBUG)