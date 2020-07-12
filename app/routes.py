from app import app, db
from flask import render_template, flash, redirect, url_for
from app.forms import LoginForm, RegistrationForm, AnswerForm, AskForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Question
from werkzeug.urls import url_parse
from flask import request
from datetime import datetime

@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html', page='Main')

@app.route('/questions')
@login_required
def questions():

    questions = current_user.received.filter_by(answered=False).order_by(-Question.timestamp).all()
    data = []
    for q in questions:
        time = get_delta(q.timestamp)
        data.append({'id':q.id, 'body':q.body, 'sender':User.query.filter_by(id=q.sender_id).first().username, 
        'time':time, 'anonymous':q.anonymous, 'picture':User.query.filter_by(id=q.sender_id).first().avatar(40)})
        print(User.query.filter_by(id=q.sender_id).first().avatar(40))
    return render_template('questions.html', page='Unanswered', data=data)

@app.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', page='Sign In', form=form)

@app.route('/logout')
def logout():

    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():

    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, name=form.name.data, 
        surname=form.surname.data, location=form.location.data, birthdate=form.birthdate.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', page='Register', form=form)

@app.route('/user/<username>', methods=['GET', 'POST'])
def user(username):

    user = User.query.filter_by(username=username).first_or_404()
    if current_user.username == username:
        return redirect(url_for('index')) # Need to be changed on 'Profile' page 
    form = AskForm()
    if form.validate_on_submit():
        print(form.body.data, form.is_anonymous.data, current_user.id, 
        User.query.filter_by(username=username).first().id)
        q = Question(body=form.body.data, anonymous=form.is_anonymous.data, sender_id=current_user.id, 
            receiver_id=User.query.filter_by(username=username).first().id, answered=False)
        db.session.add(q)
        db.session.commit()
        flash('Your question was sent!')
        return(redirect('/user/' + username))
    data = []
    questions = Question.query.filter_by(receiver_id = user.id, answered=True).order_by(-Question.answer_timestamp)
    for q in questions:
        time = get_delta(q.answer_timestamp)
        data.append({'body':q.body, 'sender':User.query.filter_by(id=q.sender_id).first().username, 
        'answer':q.answer, 'time':time, 'anonymous':q.anonymous})
    return render_template('user.html', user=user, data=data, page=user.username, date=datetime.utcnow(), form=form)

@app.route('/question/<question_id>', methods=['GET', 'POST'])
@login_required
def question(question_id):

    q = Question.query.filter_by(id=question_id).first()
    u = User.query.filter_by(id=q.sender_id).first()
    if q.answered == True or q.receiver_id != current_user.id:
        return redirect(url_for('index'))
    time = get_delta(q.timestamp)
    form = AnswerForm()
    
    if form.validate_on_submit():
        q.answered = True
        q.answer = form.answer.data
        q.answer_timestamp = datetime.utcnow()
        db.session.add(q)
        db.session.commit()
        return(redirect('/user/' + current_user.username)) # Need to be changed on 'Profile' page 
        
    return render_template('question.html', question=q, user=u, form=form, time=time, page='Answer')

def get_delta(date):

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