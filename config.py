import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'djdf1605'
    SQLALCHEMY_DATABASE_URI = 'mysql://root:djdf1605@localhost/questions'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['your-email@example.com']
    QUESTIONS_PER_PAGE = 100