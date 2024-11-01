from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'))

    profile = db.relationship('Profile', back_populates='user')

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


with app.app_context():
    db.create_all()



