from flask import Blueprint, render_template, request
from flask_login import login_required, current_user

from flask import Blueprint, render_template, request, jsonify, url_for
from flask_login import login_required, current_user

from app.models import Track, Playlist
from app.services.playlist_service import PlaylistService

library_bp = Blueprint("library", __name__)


@library_bp.route("/")
@login_required
def index():
    """
    Full page load.
    Renders the base layout with library content.
    """

    search = request.args.get("search", "").strip()
    tracks_query = Track.query

    # Apply keyword-based filtering on track name or artist
    if search:
        for keyword in search.split():
            tracks_query = tracks_query.filter(
                Track.name.ilike(f"%{keyword}%") |
                Track.artist.ilike(f"%{keyword}%")
            )

        tracks = tracks_query.all()
    else:
        tracks = Track.query.order_by(Track.name.asc()).all()

    playlists = (
        Playlist.query
        .filter_by(user_id=current_user.id)
        .order_by(Playlist.created.desc())
        .all()
    )

    PlaylistService.attach_playlist_thumbnails(playlists)

    return render_template(
        "base.html",
        tracks=tracks,
        playlists=playlists,
        search=search
    )


@library_bp.route("/library")
@login_required
def library_partial():
    """
    Partial library view.
    Used by SPA navigation without full HTML layout.
    """

    search = request.args.get("search", "").strip()
    tracks_query = Track.query

    if search:
        for keyword in search.split():
            tracks_query = tracks_query.filter(
                Track.name.ilike(f"%{keyword}%") |
                Track.artist.ilike(f"%{keyword}%")
            )

        tracks = tracks_query.all()
    else:
        tracks = Track.query.order_by(Track.name.asc()).all()

    playlists = (
        Playlist.query
        .filter_by(user_id=current_user.id)
        .order_by(Playlist.created.desc())
        .all()
    )

    PlaylistService.attach_playlist_thumbnails(playlists)

    return render_template(
        "index_partial.html",
        tracks=tracks,
        playlists=playlists,
        search=search
    )


@library_bp.route("/api/library")
@login_required
def api_library():
    """
    JSON library endpoint used by the frontend.
    Fixes: /api/library returning 404.
    """

    search = request.args.get("search", "").strip()
    tracks_query = Track.query

    if search:
        for keyword in search.split():
            tracks_query = tracks_query.filter(
                Track.name.ilike(f"%{keyword}%") |
                Track.artist.ilike(f"%{keyword}%")
            )
        tracks = tracks_query.all()
    else:
        tracks = Track.query.order_by(Track.name.asc()).all()

    # IMPORTANT: return file URLs pointing at your existing stream endpoint
    return jsonify([
        {
            "id": t.id,
            "name": t.name,
            "artist": t.artist,
            "file": url_for("stream.stream", track_id=t.id),
            "thumb": url_for("stream.thumbnail", track_id=t.id),
        }
        for t in tracks
    ])
