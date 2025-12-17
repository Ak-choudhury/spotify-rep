from flask import Flask
from app.config import Config
from app.extensions import db, login_manager
from app.models import User

from app.routes import (
    auth_bp,
    library_bp,
    playlist_bp,
    stream_bp
)

def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id: str):
        return User.query.get(int(user_id))

    # IMPORTANT: no url_prefix here
    app.register_blueprint(auth_bp)
    app.register_blueprint(library_bp)
    app.register_blueprint(playlist_bp)
    app.register_blueprint(stream_bp)

    return app
