import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from app import create_app
from app.services.music_service import MusicService
from app.config import Config

db_dir = os.path.dirname(os.path.abspath(Config.db_path))
if db_dir and not os.path.exists(db_dir):
    os.makedirs(db_dir, exist_ok=True)

thumb_dir = os.path.abspath(Config.thumbnail_path)
os.makedirs(thumb_dir, exist_ok=True)

app = create_app()

with app.app_context():
    MusicService.scan_music_library()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
