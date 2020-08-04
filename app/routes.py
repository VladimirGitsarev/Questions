from app import app, db
from flask import render_template, flash, redirect, url_for
from app.forms import LoginForm, RegistrationForm, AnswerForm, AskForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Question, followers
from werkzeug.urls import url_parse
from flask import request
from datetime import datetime
from sqlalchemy import func
import random

@app.route('/')
@app.route('/index')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    popular = User.query.join(
            followers, (followers.c.followed_id == User.id)).group_by(
            followers.c.followed_id).order_by(func.count(User.id).desc()).limit(100).all()
    random.shuffle(popular)
    questions = current_user.followed_questions().paginate(
        page, app.config['QUESTIONS_PER_PAGE'], False)
    if not questions.items:
        ids = []
        for u in popular:
            ids.append(u.id)
        questions = Question.query.filter(Question.receiver_id.in_(ids)).filter_by(answered=True)\
                      .order_by(Question.answer_timestamp.desc()).paginate(
                       page, app.config['QUESTIONS_PER_PAGE'], False)
    next_url = url_for('index', page=questions.next_num) \
        if questions.has_next else None
    prev_url = url_for('index', page=questions.prev_num) \
        if questions.has_prev else None
    return render_template('index.html', page='Main', questions=questions.items,
                           popular=popular[:5], next_url=next_url,
                           prev_url=prev_url)

@app.route('/questions')
@login_required
def questions():
    page = request.args.get('page', 1, type=int)
    questions = current_user.received.filter_by(answered=False)\
                .order_by(-Question.timestamp).paginate(
                page, app.config['QUESTIONS_PER_PAGE'], False)
    next_url = url_for('questions', page=questions.next_num) \
        if questions.has_next else None
    prev_url = url_for('questions', page=questions.prev_num) \
        if questions.has_prev else None
    return render_template('questions.html', page='Unanswered', 
                            questions=questions.items, next_url=next_url,
                            prev_url=prev_url)

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
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    if current_user.username == username:
        return redirect(url_for('index')) # Need to be changed on 'Profile' page 
    form = AskForm()
    if form.validate_on_submit():
        q = Question(body=form.body.data, anonymous=form.is_anonymous.data, sender_id=current_user.id, 
            receiver_id=User.query.filter_by(username=username).first().id, answered=False)
        db.session.add(q)
        db.session.commit()
        flash('Your question was sent!')
        return(redirect('/user/' + username))
    questions = user.received.filter_by(answered=True).order_by(-Question.answer_timestamp)\
                .paginate(page, app.config['QUESTIONS_PER_PAGE'], False)
    next_url = url_for('user', username=username, page=questions.next_num) \
        if questions.has_next else None
    prev_url = url_for('user', username=username, page=questions.prev_num) \
        if questions.has_prev else None
    return render_template('user.html', user=user, questions=questions.items, 
                            page=user.username, form=form, next_url=next_url,
                            prev_url=prev_url)

@app.route('/question/<question_id>', methods=['GET', 'POST'])
@login_required
def question(question_id):

    q = Question.query.filter_by(id=question_id).first()
    if q.answered == True or q.receiver_id != current_user.id:
        return redirect(url_for('index'))
    form = AnswerForm()
    
    if form.validate_on_submit():
        q.answered = True
        q.answer = form.answer.data
        q.answer_timestamp = datetime.utcnow()
        db.session.add(q)
        db.session.commit()
        return(redirect('/user/' + current_user.username)) # Need to be changed on 'Profile' page 
        
    return render_template('question.html', question=q, form=form, page='Answer')

@app.route('/follow/<username>')
@login_required
def follow(username):

    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    current_user.follow(user)
    db.session.commit()
    flash('You are now following {}!'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {} anymore.'.format(username))
    return redirect(url_for('user', username=username))
