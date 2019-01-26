import datetime
import json
import os

from fabric import api
from fabric.state import env
from termcolor import colored

import app
import models
import settings
import utils

env.user = "talks"
env.forward_agent = True
env.branch = "master"

env.hosts = []
env.settings = None

@api.task
def development():
    """
    Work on development branch.
    """
    env.branch = 'development'

@api.task
def master():
    """
    Work on stable branch.
    """
    env.branch = 'master'

@api.task
def branch(branch_name):
    """
    Work on any specified branch.
    """
    env.branch = branch_name

@api.task
def tests():
    """
    Run Python unit tests.
    """
    api.local('nosetests')


@api.task
def e(environment):
    env.settings = environment
    env.hosts = settings.ENVIRONMENTS[environment]['hosts']

@api.task
def checkout():
    api.run('git clone git@github.com:ireapps/%s.git /home/talks/apps/%s' % (settings.PROJECT_NAME, settings.PROJECT_NAME))

@api.task
def nginx():
    api.run('sudo service nginx reload')

@api.task
def wsgi():
    api.run('touch /home/talks/apps/%s/app.py' % settings.PROJECT_NAME)

@api.task
def svcs():
    reload_nginx()
    reload_uwsgi()

@api.task
def pull():
    api.run('cd /home/talks/apps/%s; git fetch' % settings.PROJECT_NAME)
    api.run('cd /home/talks/apps/%s; git pull origin %s' % (settings.PROJECT_NAME, env.branch))

"""
SETUP TASKS
"""

def clear_collection(collection):
    c = utils.connect(collection)
    c.remove({})

@api.task
def tally():
    app.tally()

def load_users():
    with open('tests/users.json', 'r') as readfile:
        return list(json.loads(readfile.read()))

def load_sessions():
    with open('tests/sessions.json', 'r') as readfile:
        return list(json.loads(readfile.read()))

def load_votes():
    with open('tests/votes.json', 'r') as readfile:
        return list(json.loads(readfile.read()))

@api.task
def bake():
    utils.bake()

@api.task
def fake_data():

    for collection in ['user', 'session', 'vote']:
        clear_collection(collection)

    for user_dict in load_users():
        models.User(user_dict).save()

    for session_dict in load_sessions():
        models.Session(session_dict).save()

    for vote_dict in load_votes():
        models.Vote(vote_dict).save()

    tally()

@api.task
def varnish():
    api.run('sudo service varnish restart')

@api.task
def push():
    with api.settings(warn_only=True):
        api.local('git commit -am "Baking; deploying to production."')
        api.local('git push origin master')

@api.task
def deploy():
    # bake()
    # push()
    pull()
    wsgi()

@api.task
def check_voters():
    unique = []
    duplicates = []
    for u in utils.connect('user').find({}):
        if u['fingerprint'] in unique:
            duplicates.append(u['fingerprint'])
        else:
            unique.append(u['fingerprint'])

    for d in duplicates:
        print(d)
        print([(u['name'], u['email'], u['created'], len(u['sessions_voted_for'])) for u in utils.connect('user').find({"fingerprint": d}) if len(u['sessions_voted_for']) > 0])

@api.task
def remove_fakes():
    votes = utils.connect('vote').find({})

    count = 0
    for vote in votes:
        user = utils.connect('user').find_one({"_id": vote['user']})
        if user['fingerprint'] == "2505346121":
            utils.connect('vote').remove({"user": user['_id'], "session": vote['session']})
            utils.connect('user').remove({"_id": user['_id']})
            count += 1
            print("Removed user %s, vote %s, #%s" % (user['name'], vote['_id'], count))
