from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from app.extensions import db

class AuthService:
    """
    Authentication and user creation logic.
    """

    @staticmethod
    def create_user(username: str, password: str) -> User:
        user = User(
            username=username,
            password_hash=generate_password_hash(password)
        )

        db.session.add(user)
        db.session.commit()

        return user

    @staticmethod
    def verify_credentials(username: str, password: str) -> User | None:
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            return user

        return None
