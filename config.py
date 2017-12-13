import os
import json
import logging

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = 'secret-for-dev-only'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    DEBUG = False
    LOGGING_LEVEL = logging.CRITICAL
    logging.info("Using VCAP_SERVICES...")

    if 'VCAP_SERVICES' in os.environ:
        vcap_services = os.environ['VCAP_SERVICES']
        services = json.loads(vcap_services)
        creds = services['elephantsql'][0]['credentials']
        uri = creds["uri"]
        SQLALCHEMY_DATABASE_URI = uri
        SQLALCHEMY_POOL_SIZE = 4
        SQLALCHEMY_MAX_OVERFLOW = 1


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    LOGGING_LEVEL = logging.INFO
    logging.info("Using Development...")
    uri = 'postgres://postgres:password@localhost:5432/development'
    SQLALCHEMY_DATABASE_URI = uri


class TestingConfig(Config):
    TESTING = True
    LOGGING_LEVEL = logging.CRITICAL
    logging.info("Using Test...")
    uri = 'postgres://postgres:password@localhost:5432/test'
    SQLALCHEMY_DATABASE_URI = uri
