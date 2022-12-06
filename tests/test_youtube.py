import os, spotipy
from app.spotify import Spotify
from app.youtube import Youtube
import pytest

sp = Spotify()
yt = Youtube(ydl_input_ops=ydl_opts)

ydl_opts = {  # TODO: setup as fixture
    "cookiefile": cookies_file,
    "download_archive": archive_file,
    "outtmpl": (output_location + json_out_format),
    "quiet": True,
    "ignoreerrors": True,
    "writeinfojson": store_json,
    "skip_download": True,
    "verbose": False,
    'logtostderr': False,
    }

yt_playlist_id = "PLnKNmWNuQnyzNywBaSk2nOBpFkIQ0k89v"

def test_get_youtube_songs():
    songs = yt.get_songs_from_playlist(yt_playlist_id)
    assert len(songs) > 0

def test_invalid_id_exception():
    playlist_id = "30ffs2309xcv"
    with pytest.raises(Exception):
        songs = yt.get_songs_from_playlist(playlist_id)

def test_invalid_id_exception():
    playlist_id = "30ffs2309xcv"
    with pytest.raises(Exception):
        songs = yt.get_playlist_title(playlist_id)

def test_fetch_uri():
    songs = yt.get_songs_from_playlist(yt_playlist_id)
    song_uri = sp.get_song_uri(songs[0].artist, songs[0].title)
    assert song_uri is not None
            