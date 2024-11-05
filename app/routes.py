import os

from flask import render_template, flash, redirect, url_for, current_app, jsonify
from flask_login import login_required, current_user, login_user

from app import app, login_manager
from app.forms import RegistrationForm, LoginForm, EditProfileForm
from app.models import db, User, Profile, Friendship
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


@app.route('/home')
def home():
    all_users = User.query.all()  # Получаем всех пользователей из базы данных
    return render_template('home.html', users=all_users)


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


@app.route('/user_profile/<int:user_id>')
@login_required
def user_profile(user_id):
    user = User.query.get_or_404(user_id)
    profile = user.profile  # Предполагаем, что у вас есть связь между User и Profile
    return render_template('profile.html', user=user, profile=profile, current_user=current_user)


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

                file.save(filepath)
                current_user.profile.photo = f"uploads/{filename}"

                db.session.add(current_user.profile)

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


@app.route('/add_friend/<int:friend_id>', methods=['POST'])
@login_required
def add_friend(friend_id):
    # Проверяем, не пытается ли пользователь добавить себя в друзья
    if friend_id == current_user.id:
        return jsonify({'error': 'You cannot add yourself as a friend.'}), 400

    # Проверяем, существует ли уже заявка на дружбу
    existing_request = Friendship.query.filter(
        (Friendship.user_id == current_user.id) &
        (Friendship.friend_id == friend_id)
    ).first()

    if existing_request:
        return jsonify({'error': 'Friend request already sent.'}), 400

    # Создаем новую заявку на дружбу
    new_request = Friendship(user_id=current_user.id, friend_id=friend_id, status='pending')
    db.session.add(new_request)
    db.session.commit()

    return jsonify({'message': 'Friend request sent successfully.'}), 201


@app.route('/notifications')
@login_required
def notifications():
    try:
        pending_requests = current_user.received_requests.filter_by(status='pending').all()

        if not pending_requests:
            flash("У вас нет новых заявок в друзья.", "info")

        return render_template('notifications.html', pending_requests=pending_requests)
    except Exception as e:
        print("Error loading notifications:", e)
        flash("Произошла ошибка при загрузке уведомлений.", "error")
        return redirect(url_for('home'))


@app.route('/accept_request/<int:request_id>')
@login_required
def accept_request(request_id):
    friendship = Friendship.query.get_or_404(request_id)
    if friendship.friend_id == current_user.id and friendship.status == 'pending':
        friendship.status = 'accepted'
        db.session.commit()
        flash('Заявка в друзья принята!', 'success')
    else:
        flash('Ошибка при принятии заявки.', 'danger')
    return redirect(url_for('notifications'))


@app.route('/friends', methods=['GET', 'POST'])
def friends():
    friendships = Friendship.query.filter(
        ((Friendship.user_id == current_user.id) | (Friendship.friend_id == current_user.id)),
        (Friendship.status == 'accepted')
    ).all()

    return render_template('friends.html', users=friendships)
