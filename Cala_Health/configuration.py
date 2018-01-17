class BaseConfig(object):
    'Base config class'
    DEBUG = True
    TESTING = False
    SECRET_KEY = ''


class DevelopmentConfig(BaseConfig):
    'Development environment config'
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost/cala_health'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = ''


class DeploymentConfig(BaseConfig):
    'Deployment environment config'
    DEBUG = False
