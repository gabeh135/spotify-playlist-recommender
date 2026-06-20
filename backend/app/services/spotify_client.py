import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from app.core.config import settings


class SpotifyClient:
    def __init__(self):
        self._sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=settings.spotify_client_id, client_secret=settings.spotify_client_secret))

    def search_tracks(self, query: str, limit: int) -> list[dict]:
        results = []
        offset = 0
        
        while len(results) < limit:
            batch_size = min(50, limit - len(results))
            response = self._sp.search(q=query, type="track", limit=batch_size, offset=offset)

            items = response["tracks"]["items"]
            if not items:
                break

            results.extend(items)
            offset += len(items)
        
        return results

    def get_artist_genres(self, artist_ids: list[str]) -> dict[str, list[str]]:
        genres = {}
        for i in range(0, len(artist_ids), 50):
            chunk = artist_ids[i:i+50]
            response = self._sp.artists(chunk)

            for artist in response["artists"]:
                if artist is not None:
                    genres[artist["id"]] = artist["genres"]

        return genres

    def get_playlist_tracks(self, playlist_id: str) -> list[dict]:
        tracks = []

        response = self._sp.playlist_items(playlist_id, limit=100)
        while response:
            items = [item["track"] for item in response["items"] if item["track"] is not None]
            tracks.extend(items)
            response = self._sp.next(response) if response["next"] else None
    
        return tracks
