from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from wtforms.fields.html5 import DateField
from wtforms.widgets import TextArea
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    birthdate = DateField('Birthdate')
    email = StringField('Email', validators=[DataRequired(), Email()])
    location = StringField('Location')
    link = StringField('Links')
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class AnswerForm(FlaskForm):
    answer = StringField('Answer', validators=[DataRequired(), Length(min=2, max=300)], widget=TextArea())
    submit = SubmitField('Answer')

class AskForm(FlaskForm):
    body = StringField('Ask', validators=[DataRequired(), Length(min=2, max=300)], widget=TextArea())
    is_anonymous = BooleanField('Anonymous question')
    submit = SubmitField('Ask')