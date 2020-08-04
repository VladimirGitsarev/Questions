from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from hashlib import md5
import random
from sqlalchemy import func


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

likes = db.Table('likes',
    db.Column('answer_id', db.Integer, db.ForeignKey('question.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)
    
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

    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

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

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_questions(self):
        return Question.query.filter_by(answered=True).join(
            followers, (followers.c.followed_id == Question.receiver_id)).filter(
                followers.c.follower_id == self.id).order_by(
                    Question.answer_timestamp.desc())


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(300))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    answered = db.Column(db.Boolean, nullable=False, default=False)
    answer = db.Column(db.String(300), default=None)
    answer_timestamp = db.Column(db.DateTime, default=None)
    anonymous = db.Column(db.Boolean, nullable=False, default=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    likes = db.relationship(
        'User', secondary=likes,
        primaryjoin=(likes.c.answer_id == id),
        secondaryjoin=(likes.c.user_id == User.id),
        backref=db.backref('liked', lazy='dynamic'), lazy='dynamic')    

    def __repr__(self):
        return '<Question {} from {} to {}>'.format(self.body, self.sender_id, self.receiver_id)

    def is_liked(self, user):
        print(self.likes.filter(
            likes.c.user_id == user.id).count() > 0)
        return self.likes.filter(
            likes.c.user_id == user.id).count() > 0

    def get_delta(self, answer=False):
        
        if answer:
            date = self.answer_timestamp
        else:
            date = self.timestamp
        delta = datetime.utcnow() - date
        if delta.days > 366:
            time = 'More than a year'
        elif delta.days > 30:
            time = str(delta.days // 30) + ' months'
        elif delta.days > 0:
            time = str(delta.days) + ' days'
        else:
            if delta.seconds > 3600:
                time = str(delta.seconds // 3600) + ' hours'
            elif delta.seconds > 60:
                time = str(delta.seconds // 60) + ' minutes'
            else:
                time = str(delta.seconds) + ' seconds'
        return time