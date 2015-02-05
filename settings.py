import os

PROJECT_NAME = "lightning-talks"

DEPLOYMENT_TARGET = os.environ.get('DEPLOYMENT_TARGET', 'dev')

DEBUG = True
if DEPLOYMENT_TARGET in ['prd', 'stg']:
    DEBUG = False

MONGO_DATABASE = 'lightningtalk-%s' % DEPLOYMENT_TARGET

VOTING = False

ENVIRONMENTS = {
    "stg": {
        "hosts": ['192.241.251.155']
    },
    "prd": {
        "hosts": ['104.236.202.196']
    }
}