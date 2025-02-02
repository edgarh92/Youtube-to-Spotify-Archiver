import os, spotipy
from app.tools.spotify import Spotify
from app.tools.youtube import Youtube
from app.main import url_to_id
import pytest

@pytest.fixture
def ydl_opts():
    return {
        "cookiefile": "/Users/ehernand/Downloads/www.youtube.com_cookies.txt",
        "download_archive": "archive_file",
        "outtmpl": "/tmp/%(title)s.%(ext)s",
        "quiet": True,
        "ignoreerrors": True,
        "writeinfojson": False,
        "skip_download": True,
        "verbose": False,
        'logtostderr': False,
    }

@pytest.fixture
def sp_instance():
    from app.tools.spotify import Spotify
    return Spotify()

@pytest.fixture
def youtube_instance(ydl_opts):
    from app.tools.youtube import Youtube
    return Youtube(ydl_input_ops=ydl_opts)

yt_playlist_id = "PLnKNmWNuQnyyzge-2mYIehi28b2bopegq"

def test_youtube_api_key_present(youtube_instance):
    assert youtube_instance.DEVELOPER_KEY, "Expected a valid YOUTUBE_API_KEY"

def test_youtube_api_key_missing(monkeypatch):
    monkeypatch.setenv("YOUTUBE_API_KEY", "")
    from app.tools.youtube import Youtube
    with pytest.raises(Exception):
        yt_bad = Youtube(ydl_input_ops={})
        yt_bad.get_songs_from_playlist("fake_playlist_id")

def test_get_youtube_songs(youtube_instance):
    songs = youtube_instance.get_songs_from_playlist(yt_playlist_id)
    assert len(songs) > 0

def test_invalid_id_playlist_songs(youtube_instance):
    playlist_id = "30ffs2309xcv"
    with pytest.raises(Exception):
        youtube_instance.get_songs_from_playlist(playlist_id)

def test_invalid_id_playlist_title(youtube_instance):
    playlist_id = "30ffs2309xcv"
    with pytest.raises(Exception):
        youtube_instance.get_playlist_title(playlist_id)

def test_fetch_uri(youtube_instance, sp_instance):
    songs = youtube_instance.get_songs_from_playlist(yt_playlist_id)
    song_uri = sp_instance.get_song_uri(songs[0].artist, songs[0].title)
    assert song_uri is not None

def test_url_to_id():
    playlist_id = "https://www.youtube.com/playlist?list=PLnKNmWNuQnyzNywBaSk2nOBpFkIQ0k89v"
    assert url_to_id(playlist_id) == "PLnKNmWNuQnyzNywBaSk2nOBpFkIQ0k89v"