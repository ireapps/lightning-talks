import os

DEPLOYMENT_TARGET = os.environ.get('DEPLOYMENT_TARGET', 'development')

DEBUG = True
if DEPLOYMENT_TARGET in ['production', 'staging']:
    DEBUG = False

MONGO_DATABASE = 'lightningtalk-%s' % DEPLOYMENT_TARGET

VOTING = True