from flask import Blueprint, render_template, request
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
