import os

class Config:
    """
    Centralized configuration.
    Only values that are actually used are defined here.
    """

    SECRET_KEY = os.getenv("SECRET_KEY", "local_secret_key")

    db_path = os.getenv("DB_PATH", "music.db")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    music_path = os.getenv("MUSIC_PATH", "/mnt/nas/quran")
    thumbnail_path = "/app/thumbnails"
