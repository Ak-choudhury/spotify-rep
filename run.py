import os
from app import create_app
from app.services.music_service import MusicService
from app.config import Config

if "/" in Config.db_path:
    os.makedirs(os.path.dirname(Config.db_path), exist_ok=True)

app = create_app()

os.makedirs(Config.thumbnail_path, exist_ok=True)

with app.app_context():
    MusicService.scan_music_library()

if __name__ == "__main__":
    app.run(debug=True)