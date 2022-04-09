from youtube_title_parse import get_artist_title
from googleapiclient.discovery import build
from oauth2client.tools import argparser
from ytdlp import yt_dlp
from dataclasses import dataclass
from pprint import pprint
import re
import os


@dataclass
class Song:
    artist: str
    title: str


def clean_song_info(song: Song) -> Song:
    artist, title = song.artist, song.title
    title = re.sub('\(.*', '', title)          # Remove everything after '(' including '('
    title = re.sub('ft.*', '', title)          # Remove everything after 'ft' including 'ft'
    title = re.sub(',.*', '', title)           # Remove everything after ',' including ','
    artist = re.sub('\sx\s.*', '', artist)     # Remove everything after ' x ' including ' x '
    artist = re.sub('\(.*', '', artist)        # Remove everything after '(' including '('
    artist = re.sub('ft.*', '', artist)        # Remove everything after 'ft' including 'ft'
    artist = re.sub(',.*', '', artist)         # Remove everything after ',' including ','
    return Song(artist.strip(), title.strip()) # Remove whitespaces from start and end


class Youtube:
    DEVELOPER_KEY = os.getenv('YOUTUBE_API_KEY')
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"

    def __init__(self):
        self.songs = []
        self.youtube = build(
            Youtube.YOUTUBE_API_SERVICE_NAME,
            Youtube.YOUTUBE_API_VERSION,
            developerKey=Youtube.DEVELOPER_KEY
        )

    def __fetch_songs(self, youtube, playlist_id, ydl_opts, page_token=None):
        result = youtube.playlistItems().list(
            part="snippet", 
            playlistId=playlist_id,
            maxResults="300",
            pageToken=page_token
        ).execute()

        for item in result['items']:
            song = item['snippet']['title']
            track = item['snippet']['resourceId']['videoId']
            
            try:
                ytdl = yt_dlp()
                video_info = ytdl.call_yt_dlp(track, ydl_opts)
                artist, title = ytdl.processVideoTrack(video_info)
                if artist is not None and title is not None:
                    self.songs.append(clean_song_info(Song(artist, title)))
            except:
                try:
                    artist, title = get_artist_title(song)
                    self.songs.append(clean_song_info(Song(artist, title)))
                except:
                    print(f'Error parsing Track and Title {song}')
                    print(f'Error parsing title {song}')


        return result

    def get_songs_from_playlist(self, playlist_id: str, ydl_opts):
        youtube = self.youtube
        result = self.__fetch_songs(youtube, playlist_id, ydl_opts)
        while 'nextPageToken' in result:
            page_token = result['nextPageToken']
            result = self.__fetch_songs(youtube, playlist_id, page_token)
        return self.songs


if __name__ == "__main__":
    yt = Youtube()
    print(clean_song_info(Song('Mr. x Probz', 'Waves(Robin Schulz Remix Radio Edit')))
    pprint(yt.get_songs_from_playlist('PLgzTt0k8mXzEpH7-dOCHqRZOsakqXmzmG'))
