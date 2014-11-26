import os

PROJECT_NAME = "lightning-talks"

DEPLOYMENT_TARGET = os.environ.get('DEPLOYMENT_TARGET', 'development')

DEBUG = True
if DEPLOYMENT_TARGET in ['production', 'staging']:
    DEBUG = False

MONGO_DATABASE = 'lightningtalk-%s' % DEPLOYMENT_TARGET

VOTING = True

ENVIRONMENTS = {
    "staging": {
        "hosts": ['192.241.251.155']
    }
}