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

# Edit my item?
# Checkbox: Are you going to NICAR this year?
# Route to remove my vote.
# Sort by alpha?
# Sort by most popular?
# Sort by random (default)?

@app.route('/')
def homepage():
    if settings.VOTING:

        sessions = utils.connect('session').find({})
        payload = []

        for s in sessions:
            if s.get('votes', None):
                payload.append(s)

        if len(payload) > 0:
            payload = sorted(payload, key=lambda x: x['votes'], reverse=True)

        return render_template('session_list.html', sessions=payload, VOTING=settings.VOTING)

    else:
        return render_template('create_session.html', VOTING=settings.VOTING);

@app.route('/sessions')
def session_list():
    sessions = utils.connect('session').find({})
    payload = []

    for s in sessions:
        if s.get('votes', None):
            payload.append(s)

    if len(payload) > 0:
        payload = sorted(payload, key=lambda x: x['votes'], reverse=True)

    return render_template('session_list.html', sessions=payload, VOTING=settings.VOTING)

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

    return json.dumps({"success": False, "text": "You've already voted for this session."})

@app.route('/api/vote/')
def api_vote(methods=['GET']):
    from flask import request
    _id = request.args.get('_id', None)
    if not _id:
        return json.dumps(list(utils.connect('vote').find({})))

    vote = dict(utils.connect('vote').find_one({"_id": _id}))
    return json.dumps(vote)

@app.route('/api/session/action/')
def session_action(methods=['GET']):
    from flask import request
    _id = request.args.get('user', None)
    user = None

    session_dict = {}
    session_dict['title'] = request.args.get('title', None)
    session_dict['description'] = request.args.get('description', None)
    session_dict['votes'] = 1
    session_dict['accepted'] = False

    error = json.dumps({"success": False, "text": "Please send a valid user ID and a session title and description."})

    if not _id:
        return json.dumps(error)

    if _id:
        user = dict(utils.connect('user').find_one({"_id": _id}))
        session_dict['user'] = _id
        s = models.Session(**session_dict).save()
        print s
        # models.Vote(user=u['_id'], session=s['_id']).save()

        return json.dumps({"success": True, "action": "create"})

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
    server_port = 8002

    if args.port:
        server_port = int(args.port)

    app.run(host='0.0.0.0', port=server_port, debug=settings.DEBUG)