from datetime import datetime
import json
import re
import time
from uuid import uuid4

from passlib.hash import bcrypt

class ModelClass(object):
    id = None
    created = None
    updated = None

    def __init__(self, *args, **kwargs):
        """
        Accepts either a dictionary as the first argument
        or a series of keyword arguments.
        """
        if args:
            if isinstance(args[0], dict):
                for k,v in args[0].items():
                    setattr(self, k,v)

        for k,v in kwargs.items():
            setattr(self, k, v)

        if not self.id:
            self.id = str(uuid4())

        now = datetime.now()
        for field in ['created', 'updated']:
            if not getattr(self, field):
                setattr(self, field, now)

    def __str__(self):
        return self.__unicode__()

    def __repr__(self):
        return self.__unicode__()


    def to_dict(self):
        payload = dict(self.__dict__)

        for field in ['created', 'updated']:
            payload[field] = time.mktime(getattr(self, field).timetuple())

        return payload

    def to_json(self):
        return json.dumps(self.to_dict())

    def commit_to_db(self):
        self.updated = datetime.now()
        pass

class User(ModelClass):
    name = None
    email = None
    sessions_voted_for = []
    sessions_pitched = []
    login_hash = None
    password = None

    def __unicode__(self):
        return self.name

    def auth_user(self, possible_password):
        return bcrypt.verify(possible_password, self.login_hash)

    def save(self, test=False):
        if not self.login_hash:
            if not self.password:
                raise ValueError("Password must not be null.")

            if self.password == "password":
                raise ValueError("Seriously. Seriously?")

        self.login_hash = bcrypt.encrypt(self.password)
        self.password = None

        if not test:
            self.commit_to_db()



class Session(ModelClass):
    title = None
    description = None
    user = None
    votes = 0
    users_voting_for = []
    accepted = False

    def __unicode__(self):
        return self.title

    def cast_vote(self, user):
        self.votes += 1
        self.users_voting_for.append(user)
        self.save()
        return self.votes

    def save(self, test=False):
        if not test:
            self.commit_to_db()