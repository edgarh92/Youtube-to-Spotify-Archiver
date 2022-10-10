import os, spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json
CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID,
                                                           client_secret=CLIENT_SECRET))

results = sp.search(q='PO.U.RYU - Mal', type='track', limit=10, market='US')
for idx, track in enumerate(results['tracks']['items']):
    print(idx, track['artists'][0]['name'])