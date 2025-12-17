from datetime import datetime
from app.extensions import db

class Playlist(db.Model):
    """
    User-owned playlist.
    """

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)
