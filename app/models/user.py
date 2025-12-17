from flask_login import UserMixin
from app.extensions import db

class User(UserMixin, db.Model):
    """
    Application user.
    Authentication is handled via Flask-Login.
    """

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
