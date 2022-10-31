from spotipy import util
import spotipy
import requests 
import os
from logger import setup_logger
from urllib.parse import quote
from utils import fuzzy_match_artist, artist_names_from_result
from typing import Literal, Any


class SpotifyClientManager:
    def __init__(self):
        self.scope = 'playlist-modify-private'
        self.user_id = os.getenv('SPOTIFY_USER_ID')
        self.client_id = os.getenv('SPOTIFY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        self.redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI')

    @property
    def token(self):
        '''
        Return the access token
        '''
        return util.prompt_for_user_token(
            self.user_id,
            scope=self.scope,
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri
        )


class Spotify:
    def __init__(self):
        self.spotify = SpotifyClientManager()
        self.spotify_logger = setup_logger(__name__)
        print(self.spotify.token)
    def create_playlist(self, playlist_name: str) -> str:
        request_body = {
            "name": playlist_name,
            "description": "youtube playlist",
            "public": False
        }

        query = f"https://api.spotify.com/v1/users/{self.spotify.user_id}/playlists"

        response = requests.post(
            query,
            json=request_body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.spotify.token}"
            }
        )

        playlist = response.json()
        print(response.json())
        return playlist['id']

    def get_song_uri(self, artist: str, song_name: str) -> 'str':
        track_request = quote(f'{song_name} {artist}')  # TODO: intercept None types as nulls and exit search. 
        query = f'https://api.spotify.com/v1/search?q={track_request}&type=track&limit=10'
        self.spotify_logger.debug(f'Query arguments: {query}')

        response = requests.get(
            query,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.spotify.token}"
            }
        )

        if not response.ok:
            self.spotify_logger.debug(f"Response Code: {response.ok}")
            return None

        results = response.json()

        items = results['tracks']['items']

        artist_names = artist_names_from_result(items)
        track_name = f'{artist}'
        fuzzy_match_artist(
            artist_names=artist_names,
            track_input=track_name)

        if not items:
            return None
        else:
            return items[0]['uri']

    def add_song_to_playlist(self, song_uri: str, playlist_id: str) -> bool:
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        response = requests.post(
            url,
            json={"uris": [song_uri]},
            headers={
                "Authorization": f"Bearer {self.spotify.token}",
                "Content-Type": "application/json"
            }
        )
        return response.ok

    def _num_playlist_songs(self, playlist_id) -> Any | Literal[False] | None:
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

        response = requests.get(
            url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.spotify.token}"
            }
        )

        if not response.ok:
            self.spotify_logger.error("Bad API Response")
            return response.ok

        results = response.json()
        if 'total' in results:
            return results['total']
        return None
