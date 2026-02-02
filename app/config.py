import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class Config:
    """
    Centralized configuration.
    """

    SECRET_KEY = os.getenv("SECRET_KEY", "local_secret_key")

    db_path = os.getenv("DB_PATH", os.path.join(PROJECT_ROOT, "data", "music.db"))
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


    music_path = os.getenv("MUSIC_PATH", os.path.join(PROJECT_ROOT, "music"))
    thumbnail_path = os.getenv("THUMBNAIL_PATH", os.path.join(PROJECT_ROOT, "thumbnails"))
