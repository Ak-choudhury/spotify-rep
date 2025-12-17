from app.extensions import db
from app.models import Track, PlaylistTrack

class PlaylistService:
    """
    Playlist-related business logic.
    """

    @staticmethod
    def attach_playlist_thumbnails(playlists: list) -> list:
        """
        Adds `thumb_track_id` attribute to each playlist.
        This is derived from the first track in the playlist.
        """

        for playlist in playlists:
            first_track = (
                db.session.query(Track)
                .join(PlaylistTrack, PlaylistTrack.track_id == Track.id)
                .filter(PlaylistTrack.playlist_id == playlist.id)
                .first()
            )

            playlist.thumb_track_id = first_track.id if first_track else None

        return playlists
