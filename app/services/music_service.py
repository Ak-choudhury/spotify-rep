import os
from app.extensions import db
from app.models import Track
from app.utils.thumbnail import extract_thumbnail
from app.config import Config

class MusicService:
    """
    Handles music scanning and database population.
    """

    @staticmethod
    def scan_music_library() -> None:
        """
        Scans the configured music directory and imports new MP3 files.
        """

        db.create_all()

        if not os.path.exists(Config.music_path):
            print("Music folder not found:", Config.music_path)
            return

        for filename in os.listdir(Config.music_path):
            if not filename.lower().endswith(".mp3"):
                continue

            file_path = os.path.join(Config.music_path, filename)

            # Avoid duplicate imports
            if Track.query.filter_by(file_path=file_path).first():
                continue

            track_name = os.path.splitext(filename)[0]
            thumbnail = extract_thumbnail(file_path, Config.thumbnail_path)

            track = Track(
                name=track_name,
                artist="Unknown",
                file_path=file_path,
                thumbnail_path=thumbnail
            )

            db.session.add(track)

        db.session.commit()
