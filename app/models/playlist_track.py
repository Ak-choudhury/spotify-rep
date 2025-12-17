from app.extensions import db

class PlaylistTrack(db.Model):
    """
    Association table between playlists and tracks.
    """

    id = db.Column(db.Integer, primary_key=True)
    playlist_id = db.Column(db.Integer, nullable=False)
    track_id = db.Column(db.Integer, nullable=False)
