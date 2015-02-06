import json
import os

from fabric import api
from fabric.state import env
from termcolor import colored

import models
import settings
import utils

env.user = "ubuntu"
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
    api.run('git clone git@github.com:ireapps/%s.git /home/ubuntu/%s' % (settings.PROJECT_NAME, settings.PROJECT_NAME))

@api.task
def nginx():
    api.run('sudo service nginx reload')

@api.task
def wsgi():
    api.run('touch /home/ubuntu/%s/app.py' % settings.PROJECT_NAME)

@api.task
def svcs():
    reload_nginx()
    reload_uwsgi()

@api.task
def pull():
    api.run('cd /home/ubuntu/%s; git fetch' % settings.PROJECT_NAME)
    api.run('cd /home/ubuntu/%s; git pull origin %s' % (settings.PROJECT_NAME, env.branch))

"""
SETUP TASKS
"""

def clear_collection(collection):
    c = utils.connect(collection)
    c.remove({})

@api.task
def tally():
    models.Session.tally()
    models.User.tally()

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
    api.local('git commit -am "Baking; deploying to production."')
    api.local('git push origin master')

@api.task
def deploy():
    bake()
    push()
    pull()
    wsgi()