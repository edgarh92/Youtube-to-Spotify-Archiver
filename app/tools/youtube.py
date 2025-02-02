from youtube_title_parse import get_artist_title #  TODO: Handle missing dependency 
from googleapiclient.discovery import build, Resource
from app.tools.ytdlp import VideoTitleExtractor
from dataclasses import dataclass
from pprint import pprint
import re
import os
from app.tools.app_logger import setup_logger

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
    """Builds Youtube API connection 
    Requires:
        DEVELOPER_KEY,
        YOUTUBE_API_SERVICE_NAME,
        YOUTUBE_API_VERSION

    Raises:
        YtDlpParseError: _description_
        SongInfoNotFound: _description_

    """    
    DEVELOPER_KEY = os.getenv('YOUTUBE_API_KEY')
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"

    def __init__(self, ydl_input_ops: dict):
        self.songs = []
        self.youtube = build(
            Youtube.YOUTUBE_API_SERVICE_NAME,
            Youtube.YOUTUBE_API_VERSION,
            developerKey=Youtube.DEVELOPER_KEY
        )
        self.ytdl = VideoTitleExtractor(ydl_input_ops)
        self.yt_logger = setup_logger(__name__)

    def __get_artist_title_ytdlp(self, video_id):
        video_info = self.ytdl.get_yt_metadata(video_id)
        track_info = {}

        track_info['artist'],track_info['title'] = self.ytdl.process_video_track(
            video_info)
        if track_info['artist'] and track_info['title']:
            return track_info
        else:
            return None

    def __fetch_playlist_name(self, youtube: Resource, playlist_id, page_token=None) -> str:
        '''
        Args:
            youtube (Youtube): Youtube API Class
            playlist_id (string): String identifier of playlist. 
            page_token (_type_, optional): _description_. Defaults to None.

        Returns:
            result: contains nextPageToken if more than 300 items were found.
        '''
        self.yt_logger.debug(f"Fetching playlist name for ID: {playlist_id}")
        result = youtube.playlists().list(
            part="snippet", 
            id=playlist_id,
            maxResults="300",
            pageToken=page_token
        ).execute()
        self.yt_logger.debug(f"Playlist name result: {result['items'][0]['snippet']['title']}")
        return result['items'][0]['snippet']['title']

    def __fetch_songs(self, youtube: Resource, playlist_id, page_token=None):
        """
        Calls Youtube API playlistItems to obtain title and video id and populate song list (@ Youtube.songs)
        Parses the title to obtain artist and song name. 
        Priority via yt-dlp first for song and artist metadata. 
        Fallback to youtube_title_parser libary to obtain song,artist

        Args:
            youtube (Youtube): Youtube API Class
            playlist_id (string): String identifier of playlist. 
            ydl_input_ops (Dict): Arguments of yt-dlp command line call. 
            page_token (_type_, optional): _description_. Defaults to None.

        Returns:
            result: contains nextPageToken if more than 300 items were found. 
        """
        self.yt_logger.debug(f"Fetching songs for playlist: {playlist_id} PageToken: {page_token}")
        result = youtube.playlistItems().list(
            part="snippet", 
            playlistId=playlist_id,
            maxResults="300",
            pageToken=page_token
        ).execute()
        for item in result['items']:
            api_song_title = item['snippet']['title']
            video_id = item['snippet']['resourceId']['videoId']
            self.yt_logger.debug(f"API Title: {api_song_title}, Video ID: {video_id}")
            print(
                f'Youtube API - Title {api_song_title} Video ID {video_id}')
            try:
                track_info = self.__get_artist_title_ytdlp(
                    video_id,)
                if not track_info:
                    self.yt_logger.debug(
                        f"No track info found - Title {api_song_title} - Video ID {video_id}") 
                    raise YtDlpParseError
                else:
                    self.songs.append(clean_song_info(
                        Song(
                            str(track_info['artist']),
                            str(track_info['title'])))
                            )

            except YtDlpParseError:
                try:  # TODO: Handle none for artist. 
                    artist, title = get_artist_title(api_song_title)
                    if not artist or not title:
                        raise SongInfoNotFound
                    else:
                        self.songs.append(clean_song_info(
                            Song(str(artist), str(title))))
                except TypeError as SongInfoNotFound:
                    print(f'Error parsing Track and Title {api_song_title}')
                    print(f'Error parsing title {api_song_title}')
        self.yt_logger.debug(f"Fetched {len(result['items'])} items from playlist.")
        return result

    def get_songs_from_playlist(self, playlist_id: str):
        """Execute search for video items from playlistItems or YoutubeDLP
        Args:
            playlist_id (str): Youtube Playilst ID
        Returns:
            songs (list): list of all songs found using ytldp or Youtube API
        """        
        youtube = self.youtube
        result = self.__fetch_songs(youtube, playlist_id)
        while 'nextPageToken' in result:  # Executes until no more pages.
            page_token = result['nextPageToken']
            result = self.__fetch_songs(youtube, playlist_id, page_token)
        return self.songs

    def get_playlist_title(self, playlist_id: str):
        """_summary_

        Args:
             playlist_id (str): Youtube Playilst ID

        Returns:
            playist_title (str): The playlist's title.
        """        
        youtube = self.youtube
        return self.__fetch_playlist_name(youtube, playlist_id)

if __name__ == "__main__":
    yt = Youtube()
    
    print(clean_song_info(Song('Mr. x Probz', 'Waves(Robin Schulz Remix Radio Edit')))
    pprint(yt.get_songs_from_playlist('PLgzTt0k8mXzEpH7-dOCHqRZOsakqXmzmG'))
