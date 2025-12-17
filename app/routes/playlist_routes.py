from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user

from app.extensions import db
from app.models import Playlist, Track, PlaylistTrack
from app.services.playlist_service import PlaylistService

playlist_bp = Blueprint("playlist", __name__)


@playlist_bp.route("/playlist/create", methods=["POST"])
@login_required
def playlist_create():
    """
    Creates a new playlist for the current user.
    """

    name = request.form["name"].strip()

    if not name:
        return "Invalid name", 400

    playlist = Playlist(
        name=name,
        user_id=current_user.id
    )

    db.session.add(playlist)
    db.session.commit()

    return redirect(url_for("library.index"))


@playlist_bp.route("/playlist/<int:playlist_id>")
@login_required
def playlist_view(playlist_id: int):
    """
    Partial playlist view.
    Injected into SPA content container.
    """

    playlist = Playlist.query.filter_by(
        id=playlist_id,
        user_id=current_user.id
    ).first_or_404()

    tracks = (
        db.session.query(Track)
        .join(PlaylistTrack, PlaylistTrack.track_id == Track.id)
        .filter(PlaylistTrack.playlist_id == playlist_id)
        .all()
    )

    playlists = (
        Playlist.query
        .filter_by(user_id=current_user.id)
        .order_by(Playlist.created.desc())
        .all()
    )

    PlaylistService.attach_playlist_thumbnails(playlists)

    return render_template(
        "playlist_partial.html",
        playlist=playlist,
        tracks=tracks,
        playlists=playlists
    )


@playlist_bp.route("/playlist/<int:playlist_id>/add/<int:track_id>")
@login_required
def playlist_add(playlist_id: int, track_id: int):
    """
    Adds a track to a playlist.
    """

    playlist = Playlist.query.filter_by(
        id=playlist_id,
        user_id=current_user.id
    ).first()

    if not playlist:
        return "Forbidden", 403

    exists = PlaylistTrack.query.filter_by(
        playlist_id=playlist_id,
        track_id=track_id
    ).first()

    if not exists:
        db.session.add(
            PlaylistTrack(
                playlist_id=playlist_id,
                track_id=track_id
            )
        )
        db.session.commit()

    return redirect(url_for("library.index"))


@playlist_bp.route("/playlist/<int:playlist_id>/remove/<int:track_id>")
@login_required
def playlist_remove(playlist_id: int, track_id: int):
    """
    Removes a track from a playlist.
    """

    row = PlaylistTrack.query.filter_by(
        playlist_id=playlist_id,
        track_id=track_id
    ).first()

    if row:
        db.session.delete(row)
        db.session.commit()

    return redirect(url_for("library.index"))


@playlist_bp.route("/playlist/<int:playlist_id>/delete", methods=["GET", "POST"])
@login_required
def playlist_delete(playlist_id: int):
    """
    Deletes a playlist and all its track associations.
    """

    playlist = Playlist.query.filter_by(
        id=playlist_id,
        user_id=current_user.id
    ).first_or_404()

    PlaylistTrack.query.filter_by(
        playlist_id=playlist_id
    ).delete()

    db.session.delete(playlist)
    db.session.commit()

    return redirect(url_for("library.index"))
