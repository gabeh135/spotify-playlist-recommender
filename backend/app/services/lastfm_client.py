import time

import httpx

from app.core.config import settings


class LastFmClient:
    def __init__(self):
        self._api_key = settings.lastfm_api_key
        self._base_url = "http://ws.audioscrobbler.com/2.0/"
        self._client = httpx.Client()

    def get_track_tags(self, artist: str, title: str, limit: int = 10) -> list[str]:
        params = {
            "method": "track.getTopTags",
            "artist": artist,
            "track": title,
            "api_key": self._api_key,
            "format": "json",
        }
        response = self._client.get(self._base_url, params=params).json()

        if "error" in response:
            return []

        raw = response.get("toptags", {}).get("tag", [])
        if not raw:
            return []

        # necessary as Last.fm returns an object instead of a list when there's only one tag
        tags = raw if isinstance(raw, list) else [raw]
        return [tag["name"].lower() for tag in tags[:limit]]

    def get_track_tags_batch(
        self, tracks: list[tuple[str, str]], limit: int = 10
    ) -> dict[tuple[str, str], list[str]]:
        results = {}

        for artist, title in tracks:
            results[(artist, title)] = self.get_track_tags(artist, title, limit)

            # avoid rate limiting with Last.fm's API
            time.sleep(0.2)

        return results
