import os

from flask import render_template, flash, redirect, url_for, current_app
from flask_login import login_required, current_user, login_user

from app import app, login_manager
from app.forms import RegistrationForm, LoginForm, EditProfileForm
from app.models import db, User, Profile
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Имя пользователя уже занято. Пожалуйста, выберите другое.', 'error')
            return redirect(url_for('register'))

        user = User(username=username)
        user.set_password(password)

        profile = Profile()
        user.profile = profile

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
    return render_template('profile.html', user=current_user, profile=current_user.profile)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        # Обновите профиль текущего пользователя
        current_user.profile.bio = form.bio.data
        current_user.profile.age = form.age.data

        if form.photo.data:
            file = form.photo.data
            # Проверка, соответствует ли файл допустимым форматам
            if allowed_file(file.filename):
                filename = secure_filename(f"{current_user.id}_{file.filename}")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                print(f"UPLOAD_FOLDER: {app.config['UPLOAD_FOLDER']}")
                print(f"Filepath: {filepath}")

                file.save(filepath)
                current_user.profile.photo = f"uploads/{filename}"
                print("Photo path before commit:", current_user.profile.photo)  # Отладка

                db.session.add(current_user.profile)  # Явно добавляем профиль в сессию

            else:
                flash('Недопустимый формат файла. Пожалуйста, выберите изображение PNG, JPG, JPEG или GIF.')

        # Коммит изменений в базе данных после всех обновлений
        db.session.commit()

        flash('Profile updated successfully!')
        return redirect(url_for('profile'))

        # Предзаполнение формы текущими данными профиля
    form.bio.data = current_user.profile.bio
    form.age.data = current_user.profile.age
    return render_template('edit_profile.html', form=form, user=current_user, profile=current_user.profile)