import os


def is_production():
    return os.environ.get('APPLAUSE_WEB__ENV', '') == 'production'
