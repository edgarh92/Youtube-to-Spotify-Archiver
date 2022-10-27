from app.spotify import Spotify, SpotifyClientManager
import pytest
from requests import Response

def test_api_connection():

    sp = Spotify()
    pid = sp.create_playlist("loll")
    uri = sp.get_song_uri('flor', 'hold on')
    res = sp.add_song_to_playlist(uri, pid)
    assert res
