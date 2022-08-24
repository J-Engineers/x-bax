from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=True)
    name = db.Column(db.String(100), nullable=True)
    state_name = db.Column(db.String(100), nullable=True)
    local_government_name = db.Column(db.String(100), nullable=True)
    public_id = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.Text(), nullable=True)
    profile_photo = db.Column(db.Text(), nullable=True)
    user_type = db.Column(db.Integer, nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    is_admin = db.Column(db.Boolean)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    updated_on = db.Column(db.DateTime, onupdate=datetime.utcnow)
    tokens = db.relationship('Tokens', backref="users")

    def __repr__(self) -> str:
        return 'Users>>> {self.public_id}'


class Tokens(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted = db.Column(db.Boolean)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    updated_on = db.Column(db.DateTime, onupdate=datetime.utcnow)
    user_reg_stage = db.Column(db.Integer, unique=True, nullable=True)
    password_recovery = db.Column(db.Integer, unique=True, nullable=True)
    phone_token = db.Column(db.Integer, unique=True, nullable=True)
    email_token = db.Column(db.Integer, unique=True, nullable=True)
    user_id = db.Column(db.String(500), db.ForeignKey('users.public_id'))

    def __repr__(self) -> str:
        return 'Tokens>>> {self.token}'
