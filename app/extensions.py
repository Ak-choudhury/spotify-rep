from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Shared Flask extensions.
# They are initialized inside create_app().
db = SQLAlchemy()
login_manager = LoginManager()
