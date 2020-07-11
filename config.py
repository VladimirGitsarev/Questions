import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'djdf1605'
    SQLALCHEMY_DATABASE_URI = 'mysql://root:djdf1605@localhost/questions'
    SQLALCHEMY_TRACK_MODIFICATIONS = False