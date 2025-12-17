import os
from flask import Blueprint, send_file

from flask_login import login_required
from app.models import Track

stream_bp = Blueprint("stream", __name__)


@stream_bp.route("/stream/<int:track_id>")
@login_required
def stream(track_id: int):
    """
    Streams an MP3 file directly from disk.
    """

    track = Track.query.get(track_id)

    if not track:
        return "Not found", 404

    if not os.path.exists(track.file_path):
        return "File missing", 404

    return send_file(track.file_path, mimetype="audio/mpeg")


@stream_bp.route("/thumbnail/<int:track_id>")
@login_required
def thumbnail(track_id: int):
    """
    Serves extracted album art if it exists.
    """

    track = Track.query.get(track_id)

    if (
        track
        and track.thumbnail_path
        and os.path.exists(track.thumbnail_path)
    ):
        return send_file(track.thumbnail_path, mimetype="image/jpeg")

    return "", 404
