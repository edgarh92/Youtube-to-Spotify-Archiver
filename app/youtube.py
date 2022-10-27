from youtube_title_parse import get_artist_title
from googleapiclient.discovery import build
from ytdlp import VideoTitleExtractor
from dataclasses import dataclass
from pprint import pprint
import re
import os


@dataclass
class Song:
    artist: str
    title: str


class Error(Exception):
    """Base class for other exceptions"""
    pass


class YtDlpParseError(Error):
    '''Raised when yt-dlp library does not contain information needed'''
    pass


class SongInfoNotFound(Error):
    ''' Raised when no artist or song info is found'''
    pass


def clean_song_info(song: Song) -> type(Song):
    """Removes common noise in string of a track

    Args:
        song (Song): Describes artsit and title as track string type

    Returns:
        Song: Cleaned up dataclass
   Examples:
            >>> clean_song_info('Macroblank', '痛みの永 ft Kamo (痛)')
                Song.artist('Macroblank')
                Song.title('痛みの永 Kamo')
    """
    artist, title = song.artist, song.title
    title = re.sub('\(.*', '', title)          # Remove everything after '(' including '('
    title = re.sub('ft.*', '', title)          # Remove everything after 'ft' including 'ft'
    title = re.sub(',.*', '', title)           # Remove everything after ',' including ','
    artist = re.sub('\sx\s.*', '', artist)     # Remove everything after ' x ' including ' x '
    artist = re.sub('\(.*', '', artist)        # Remove everything after '(' including '('
    artist = re.sub('ft.*', '', artist)        # Remove everything after 'ft' including 'ft'
    artist = re.sub(',.*', '', artist)         # Remove everything after ',' including ','
    return Song(artist.strip(), title.strip())  # Remove whitespaces from start and end


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

    def __get_artist_title_ytdlp(self, video_id, ydl_opts):
        ytdl = VideoTitleExtractor()
        video_info = ytdl.call_yt_dlp(video_id, ydl_opts)
        track_info = {}

        track_info['artist'], track_info['title'] = ytdl.process_video_track(
            video_info)
        if track_info['artist'] and track_info['title']:
            return track_info
        else:
            return None

    def __fetch_songs(self, youtube, playlist_id, ydl_opts, page_token=None):
        """
        Calls Youtube API playlistItems to obtain title and video id
        Parses the title to obtain artist and song name. 
        Priority via yt-dlp first for song and artist metadata. 
        Fallback to youtube_title_parser libary to obtain song,artist

        Args:
            youtube (Youtube): Youtube API Class
            playlist_id (string): String identifier of playlist. 
            ydl_opts (Dict): Arguments of yt-dlp command line call. 
            page_token (_type_, optional): _description_. Defaults to None.

        Returns:
            result: contains nextPageToken if more than 300 items were found. 
        """
        result = youtube.playlistItems().list(
            part="snippet", 
            playlistId=playlist_id,
            maxResults="300",
            pageToken=page_token
        ).execute()
        for item in result['items']:
            song_api_data = item['snippet']['title']
            video_id = item['snippet']['resourceId']['videoId']
            print(f'Youtube API Info: {song_api_data}, {video_id}')
            try:
                track_info = self.__get_artist_title_ytdlp(
                    video_id,
                    ydl_opts)
                if not track_info:
                    raise YtDlpParseError
                else:
                    self.songs.append(clean_song_info(
                        Song(
                            str(track_info['artist']),
                            str(track_info['title'])))
                            )

            except YtDlpParseError:
                try:  #  TODO: Handle none for artist. 
                    artist, title = get_artist_title(song_api_data)
                    if not artist or not title:
                        raise SongInfoNotFound
                    else:
                        self.songs.append(clean_song_info(
                            Song(str(artist), str(title))))
                except SongInfoNotFound:
                    print(f'Error parsing Track and Title {song_api_data}')
                    print(f'Error parsing title {song_api_data}')
        return result

    def get_songs_from_playlist(self, playlist_id: str, ydl_opts):
        youtube = self.youtube
        result = self.__fetch_songs(youtube, playlist_id, ydl_opts)
        while 'nextPageToken' in result:  # Executes until no more pages.
            page_token = result['nextPageToken']
            result = self.__fetch_songs(youtube, playlist_id, page_token)
        return self.songs


if __name__ == "__main__":
    yt = Youtube()
    print(clean_song_info(Song('Mr. x Probz', 'Waves(Robin Schulz Remix Radio Edit')))
    pprint(yt.get_songs_from_playlist('PLgzTt0k8mXzEpH7-dOCHqRZOsakqXmzmG'))