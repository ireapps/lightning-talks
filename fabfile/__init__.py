from fabric.api import local, require, settings, task
from fabric.state import env
from termcolor import colored

from models import User, Session


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

@task
def bootstrap():
    """
    Bootstrap with initial data.
    """
    users = [{
        "name": "jeremy bowers",
        "email": "jeremy.bowers@fake.fake",
        "password": "jeremybowerspassword"
    },{
        "name": "jeremy merrill",
        "email": "jeremy.merrill@fake.fake",
        "password": "jeremymerrillpassword"
    },{
        "name": "jeremy ashkenas",
        "email": "jeremy.ashkenas@fake.fake",
        "password": "jeremyashkenaspassword"
    }]

    for user_dict in users:
        u = User(user_dict)
        u.save()