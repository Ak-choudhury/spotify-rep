from app.extensions import db

class Track(db.Model):
    """
    Represents a single audio track stored on disk.
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    artist = db.Column(db.String(150), nullable=False)
    file_path = db.Column(db.String(300), nullable=False)
    thumbnail_path = db.Column(db.String(300))
