from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user, login_user
from werkzeug.security import check_password_hash

from app import app, login_manager
from app.forms import RegistrationForm, LoginForm
from app.models import db, User


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User(username=username)
        user.set_password(password)  # Устанавливаем хэш пароля

        db.session.add(user)
        db.session.commit()
        flash('User registered successfully!')

        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully!')
            return redirect(url_for('profile'))
        else:
            flash('Invalid username or password')

    return render_template('login.html', form=form)


@app.route('/profile')
@login_required
def profile():
    return f'Welcome, {current_user.username}!'
