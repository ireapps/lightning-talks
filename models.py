from datetime import datetime
import json
import os
import re
import time
from uuid import uuid4

from passlib.hash import bcrypt

import settings
import utils


class ModelClass(object):
    _id = None
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

        if not self._id:
            self._id = str(uuid4())

        now = time.mktime(datetime.now().timetuple())
        for field in ['created', 'updated']:
            if not getattr(self, field):
                setattr(self, field, now)

    def __getitem__(self, key):
        return getattr(self, key)

    def __str__(self):
        return self.__unicode__()

    def __repr__(self):
        return self.__unicode__()

    def to_dict(self):
        return dict(self.__dict__)

    def to_json(self):
        return json.dumps(self.to_dict())

    def commit_to_db(self, collection):
        self.updated = time.mktime(datetime.now().timetuple())
        collection = utils.connect(collection)
        result = collection.save(self.to_dict())
        return result


class User(ModelClass):
    name = None
    email = None
    sessions_voted_for = []
    sessions_pitched = []
    login_hash = None
    password = None
    fingerprint = None

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
            self.commit_to_db('user')

        return self

    def update_records(self):
        votes = utils.connect('vote')
        sessions = utils.connect('session')
        self.sessions_voted_for = [x['session'] for x in list(votes.find({"user": self._id}))]
        self.sessions_pitched = [x['_id'] for x in list(sessions.find({"user": self._id}))]
        self.save()

    @staticmethod
    def tally():
        collection = utils.connect('user')
        users = list(collection.find({}))

        for user_dict in users:
            u = User(user_dict)
            u.update_records()

        print "Updated %s users." % len(users)


class Session(ModelClass):
    title = None
    description = None
    user = None
    accepted = False
    votes = 0

    def __unicode__(self):
        return self.title

    def save(self, test=False):
        if not test:
            self.commit_to_db('session')

        return self

    def update_records(self):
        votes = utils.connect('vote')
        self.votes = votes.find({"session": self._id}).count()
        self.save()

    @staticmethod
    def tally():
        collection = utils.connect('session')
        sessions = list(collection.find({}))

        for session_dict in sessions:
            s = Session(session_dict)
            s.update_records()

        print "Updated %s sessions." % len(sessions)

class Vote(ModelClass):
    user = None
    session = None

    def __unicode__(self):
        return "%s,%s" % (self.user, self.session)

    def save(self, test=False):
        if not test:
            self.commit_to_db('vote')

        return self
