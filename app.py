from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user,
    login_required, logout_user, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'local_secret_key'

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///music.db'
db = SQLAlchemy(app)

# Login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# MODELS
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password_hash = db.Column(db.String(150))


class Track(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    artist = db.Column(db.String(150))
    file_path = db.Column(db.String(300))
    thumbnail_path = db.Column(db.String(300), nullable=True)


class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    name = db.Column(db.String(150))
    created = db.Column(db.DateTime, default=datetime.utcnow)


class PlaylistTrack(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    playlist_id = db.Column(db.Integer)
    track_id = db.Column(db.Integer)


# USER LOADER
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# THUMBNAIL EXTRACTION
def extract_thumbnail(mp3_path, output_folder='thumbnails'):
    os.makedirs(output_folder, exist_ok=True)
    try:
        audio = MP3(mp3_path, ID3=ID3)
        if audio.tags is None:
            return None

        for tag in audio.tags.values():
            if isinstance(tag, APIC):
                ext = tag.mime.split('/')[-1]
                filename = os.path.splitext(os.path.basename(mp3_path))[0] + f'.{ext}'
                thumb_path = os.path.join(output_folder, filename)

                with open(thumb_path, 'wb') as img:
                    img.write(tag.data)
                return thumb_path
    except Exception:
        return None

    return None


def attach_playlist_thumbs(playlists):
    """Attach .thumb_track_id attribute to each playlist (first track's id or None)."""
    for p in playlists:
        first_track = (
            db.session.query(Track)
            .join(PlaylistTrack, PlaylistTrack.track_id == Track.id)
            .filter(PlaylistTrack.playlist_id == p.id)
            .first()
        )
        p.thumb_track_id = first_track.id if first_track else None
    return playlists


# ROUTES
@app.route('/')
@login_required
def index():
    """Initial full-page load – renders base layout with library inside."""
    search = request.args.get("search", "").strip()
    tracks_query = Track.query

    if search:
        keywords = search.split()
        for kw in keywords:
            tracks_query = tracks_query.filter(
                Track.name.ilike(f"%{kw}%") |
                Track.artist.ilike(f"%{kw}%")
            )
        tracks = tracks_query.all()
    else:
        tracks = Track.query.order_by(Track.name.asc()).all()

    playlists = Playlist.query.filter_by(user_id=current_user.id).order_by(Playlist.created.desc()).all()
    attach_playlist_thumbs(playlists)

    return render_template(
        "base.html",
        tracks=tracks,
        playlists=playlists,
        search=search
    )


@app.route('/library')
@login_required
def library_partial():
    """Partial library view for SPA navigation (no <html> wrapper)."""
    search = request.args.get("search", "").strip()
    tracks_query = Track.query

    if search:
        keywords = search.split()
        for kw in keywords:
            tracks_query = tracks_query.filter(
                Track.name.ilike(f"%{kw}%") |
                Track.artist.ilike(f"%{kw}%")
            )
        tracks = tracks_query.all()
    else:
        tracks = Track.query.order_by(Track.name.asc()).all()

    playlists = Playlist.query.filter_by(user_id=current_user.id).order_by(Playlist.created.desc()).all()
    attach_playlist_thumbs(playlists)

    return render_template(
        "index_partial.html",
        tracks=tracks,
        playlists=playlists,
        search=search
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for("index"))
        else:
            error = "Invalid username or password"

    return render_template("login.html", error=error)


@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if User.query.filter_by(username=username).first():
            error = "Username already exists"
        else:
            new_user = User(
                username=username,
                password_hash=generate_password_hash(password)
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for("index"))

    return render_template("register.html", error=error)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# STREAMING
@app.route('/stream/<int:track_id>')
@login_required
def stream(track_id):
    track = Track.query.get(track_id)
    if not track:
        return "Not found", 404
    if not os.path.exists(track.file_path):
        return "File missing", 404
    return send_file(track.file_path, mimetype="audio/mpeg")


@app.route('/thumbnail/<int:track_id>')
@login_required
def thumbnail(track_id):
    track = Track.query.get(track_id)
    if track and track.thumbnail_path and os.path.exists(track.thumbnail_path):
        return send_file(track.thumbnail_path, mimetype="image/jpeg")
    return "", 404


# PLAYLIST ROUTES
@app.route('/playlist/create', methods=['POST'])
@login_required
def playlist_create():
    name = request.form["name"].strip()
    if not name:
        return "Invalid name", 400

    p = Playlist(name=name, user_id=current_user.id)
    db.session.add(p)
    db.session.commit()

    return redirect(url_for("index"))


@app.route('/playlist/<int:playlist_id>')
@login_required
def playlist_view(playlist_id):
    """Partial playlist view for SPA (goes into #content)."""
    playlist = Playlist.query.filter_by(id=playlist_id, user_id=current_user.id).first_or_404()

    tracks = (
        db.session.query(Track)
        .join(PlaylistTrack, PlaylistTrack.track_id == Track.id)
        .filter(PlaylistTrack.playlist_id == playlist_id)
        .all()
    )

    playlists = Playlist.query.filter_by(user_id=current_user.id).order_by(Playlist.created.desc()).all()
    attach_playlist_thumbs(playlists)

    return render_template(
        "playlist_partial.html",
        playlist=playlist,
        tracks=tracks,
        playlists=playlists
    )


@app.route('/playlist/<int:playlist_id>/add/<int:track_id>')
@login_required
def playlist_add(playlist_id, track_id):
    if not Playlist.query.filter_by(id=playlist_id, user_id=current_user.id).first():
        return "Forbidden", 403

    exists = PlaylistTrack.query.filter_by(playlist_id=playlist_id, track_id=track_id).first()
    if not exists:
        db.session.add(PlaylistTrack(playlist_id=playlist_id, track_id=track_id))
        db.session.commit()

    return redirect(url_for("index"))


@app.route('/playlist/<int:playlist_id>/remove/<int:track_id>')
@login_required
def playlist_remove(playlist_id, track_id):
    row = PlaylistTrack.query.filter_by(playlist_id=playlist_id, track_id=track_id).first()
    if row:
        db.session.delete(row)
        db.session.commit()
    return redirect(url_for("index"))


@app.route('/playlist/<int:playlist_id>/delete', methods=['GET', 'POST'])
@login_required
def playlist_delete(playlist_id):
    playlist = Playlist.query.filter_by(id=playlist_id, user_id=current_user.id).first_or_404()
    PlaylistTrack.query.filter_by(playlist_id=playlist_id).delete()
    db.session.delete(playlist)
    db.session.commit()
    return redirect(url_for('index'))


# AUTO IMPORT
def init_db():
    db.create_all()

    music_folder = r"Z:\shared\quran"
    if not os.path.exists(music_folder):
        print("NAS folder not found:", music_folder)
        return

    for file in os.listdir(music_folder):
        if file.lower().endswith(".mp3"):
            file_path = os.path.join(music_folder, file)
            if Track.query.filter_by(file_path=file_path).first():
                continue

            name = os.path.splitext(file)[0]
            thumb = extract_thumbnail(file_path)
            track = Track(name=name, artist="Unknown", file_path=file_path, thumbnail_path=thumb)
            db.session.add(track)

    db.session.commit()


if __name__ == "__main__":
    os.makedirs("thumbnails", exist_ok=True)

    with app.app_context():
        init_db()

    app.run(debug=True)
