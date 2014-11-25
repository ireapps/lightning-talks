import json
import os

from fabric.api import local, require, settings, task
from fabric.state import env
from pymongo import MongoClient
from termcolor import colored

from models import User, Session, Vote, update_all_sessions, update_all_users, connect

DEPLOYMENT_TARGET = os.environ.get('DEPLOYMENT_TARGET', 'development')
MONGO_DATABASE = 'lightningtalk-%s' % DEPLOYMENT_TARGET

env.user = "ubuntu"
env.forward_agent = True

env.hosts = []

@task
def development():
    """
    Work on development branch.
    """
    env.branch = 'development'

@task
def master():
    """
    Work on stable branch.
    """
    env.branch = 'master'

@task
def branch(branch_name):
    """
    Work on any specified branch.
    """
    env.branch = branch_name

@task
def tests():
    """
    Run Python unit tests.
    """
    local('nosetests')

def clear_collection(collection):
    client = MongoClient()
    db = client[MONGO_DATABASE]
    collection = db[collection]
    collection.remove({})

@task
def get_updates():
    update_all_sessions()
    update_all_users()

def load_users():
    with open('tests/users.json', 'r') as readfile:
        return list(json.loads(readfile.read()))

def load_sessions():
    with open('tests/sessions.json', 'r') as readfile:
        return list(json.loads(readfile.read()))

def load_votes():
    with open('tests/votes.json', 'r') as readfile:
        return list(json.loads(readfile.read()))

@task
def fake_data():

    for collection in ['user', 'session', 'vote']:
        clear_collection(collection)

    for user_dict in load_users():
        User(user_dict).save()

    for session_dict in load_sessions():
        Session(session_dict).save()

    for vote_dict in load_votes():
        Vote(vote_dict).save()

    get_updates()