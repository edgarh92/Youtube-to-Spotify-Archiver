import pytest
from unittest.mock import patch, MagicMock
from spotipy import util
import requests 
import os
from app_logger import setup_logger
from urllib.parse import quote
from utils import fuzzy_match_artist, artist_names_from_tracks
from Spotify import Spotify

class TestSpotify:
    @patch.object(util, 'prompt_for_user_token')
    @patch.object(requests, 'post')
    def test_create_playlist(self, mock_post, mock_prompt_for_user_token):
        mock_prompt_for_user_token.return_value = 'test_token'
        mock_response = MagicMock()
        mock_response.json.return_value = {'id': 'test_playlist_id'}
        mock_post.return_value = mock_response
        spotify = Spotify()
        playlist_id = spotify.create_playlist('test_playlist')
        assert playlist_id == 'test_playlist_id'

    @patch.object(requests, 'get_song_uri')
    def test_get_song_uri(self, mock_get):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {'tracks': {'items': [{'uri': 'test_song_uri'}]}}
        mock_get.return_value = mock_response
        spotify = Spotify()
        song_uri = spotify.get_song_uri('test_artist', 'test_song')
        assert song_uri == mock_get.json.return_value['tracks']['items'][0]['uri']  

    @patch.object(requests, 'post')
    def test_add_song_to_playlist(self, mock_post):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_post.return_value = mock_response
        spotify = Spotify()
        result = spotify.add_song_to_playlist('test_song_uri', 'test_playlist_id')
        assert result == True

