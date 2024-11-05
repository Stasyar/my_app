from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from flask_login import UserMixin

from datetime import datetime


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'))

    profile = db.relationship('Profile', back_populates='user')
    # Заявки, отправленные текущим пользователем
    sent_requests = db.relationship(
        'Friendship',
        foreign_keys='Friendship.user_id',
        backref='requester',
        lazy='dynamic'
    )

    # Заявки, полученные текущим пользователем
    received_requests = db.relationship(
        'Friendship',
        foreign_keys='Friendship.friend_id',
        backref='receiver',
        lazy='dynamic'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Profile(db.Model):
    __tablename__ = 'profiles'

    id = db.Column(db.Integer, primary_key=True)
    bio = db.Column(db.String(200), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    photo = db.Column(db.String(120))

    # Связь с пользователем (один к одному)
    user = db.relationship('User', back_populates='profile', uselist=False)


class Friendship(db.Model):
    __tablename__ = 'friendships'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"))
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"))
    status = db.Column(db.String(20), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Чтобы предотвратить дублирование, добавим уникальное ограничение
    __table_args__ = (db.UniqueConstraint('user_id', 'friend_id', name='_user_friend_uc'),)



with app.app_context():
    db.create_all()



