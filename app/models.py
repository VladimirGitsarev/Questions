from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from hashlib import md5

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
    
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(50), default=None)
    birthdate = db.Column(db.DateTime, default=None)
    link = db.Column(db.String(100), default=None)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    sent = db.relationship('Question', backref='sender', lazy='dynamic', 
        foreign_keys='Question.sender_id')
    received = db.relationship('Question', backref='receiver', lazy='dynamic', 
        foreign_keys='Question.receiver_id')

    def __repr__(self):
        return '<User {}>'.format(self.username) 

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(300))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    answered = db.Column(db.Boolean, nullable=False)
    answer = db.Column(db.String(300), default=None)
    answer_timestamp = db.Column(db.DateTime, default=None)
    anonymous = db.Column(db.Boolean, nullable=False, default=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Question {} from {} to {}>'.format(self.body, self.sender_id, self.receiver_id)