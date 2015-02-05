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
env.branch = "masterf"

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

def make_directories():
    api.run('mkdir -p /home/ubuntu/%s' % settings.PROJECT_NAME)
    api.run('sudo mkdir /var/log/%s' % settings.PROJECT_NAME)
    api.run('sudo touch /var/log/%s/uwsgi.log && chmod 777 /var/log/%s/uwsgi.log' % (settings.PROJECT_NAME, settings.PROJECT_NAME))
    api.run('sudo touch /tmp/%s.uwsgi.sock && chmod 777 /tmp/%s.uwsgi.sock' % (settings.PROJECT_NAME, settings.PROJECT_NAME))

def make_virtualenv():
    api.run('mkvirtualenv %s' % (settings.PROJECT_NAME))

@api.task
def checkout_project():
    api.run('git clone git@github.com:ireapps/%s.git /home/ubuntu/%s' % (settings.PROJECT_NAME, settings.PROJECT_NAME))

@api.task
def reload_nginx():
    api.run('sudo service nginx reload')

@api.task
def reload_uwsgi():
    api.run('sudo service %s restart' % settings.PROJECT_NAME)

@api.task
def reload_services():
    reload_nginx()
    reload_uwsgi()

@api.task
def link_confs():
    api.run('sudo cp /home/ubuntu/%s/confs/uwsgi.conf /etc/init/%s.conf' % (settings.PROJECT_NAME, settings.PROJECT_NAME))
    api.run('sudo initctl reload-configuration')


@api.task
def update_project():
    api.run('cd /home/ubuntu/%s; git fetch' % settings.PROJECT_NAME)
    api.run('cd /home/ubuntu/%s; git pull origin %s' % (settings.PROJECT_NAME, env.branch))

@api.task
def setup():
    with api.settings(warn_only=True):
        make_directories()
        make_virtualenv()
        checkout_project()
        update_project()
        install_requirements()
        link_confs()
        reload_services()

"""
SETUP TASKS
"""

def clear_collection(collection):
    collection = utils.connect(collection)
    collection.remove({})

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