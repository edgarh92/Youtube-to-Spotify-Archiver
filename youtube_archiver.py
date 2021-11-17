import json
import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import requests
import youtube_dl
import argparse
import configparser




from datetime import datetime
from youtube_title_parse import get_artist_title
import youtube_title_parse
path = os.path.abspath(youtube_title_parse.__file__)
print(path)


from exceptions import ResponseException
from secrets import spotify_token, spotify_user_id


class CreatePlaylist:
    def __init__(self):
        #self.youtube_client = self.get_youtube_client()
        self.all_song_info = {}

    def get_args(self):
        year_month = datetime.now().strftime("%Y %m")
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--url",
             "-u",
            type=str,
            required=True,
            help="Link to Video or Song URL",
            )
        parser.add_argument(
            "-o",
            "--output",
            type=str,
            default="~/Music/JSON",
            required=False,
            help="Destination location of JSON files",
        )
        parser.add_argument(
            "--dryrun",
            action="store_false",
            required=False,
            help="Do not add to Spotify and download.",
        )
        parser.add_argument(
            "-playlist",
            "--playlist",
            type=str,
            default=year_month,
            required=False,
            help="Save to specific Spotify Playlist (Default: Youtube Playlist Name)",
        )
        parser.add_argument(
            "--store_json",
            action="store_true",
            help="Download json the video."
        )

        parser.add_argument(
            "--archive",
            "--a",
            type=str,
            required=False,
            default="~/Music/JSON/archive.log",
            help="Location of archive reference file",
        )
        parser.add_argument(
            "--spotify_token",
            type=str,
            required=False,
            help="Spotify API Key.",
        )
        parser.add_argument(
            "--cookies",
            type=str,
            required=True,
            help="Cookies file"
        )

        args = parser.parse_args()
        youtube_url = args.url
        cookies_file = args.cookies
        playlist_name = args.playlist

        ydl_opts = self.build_ydl_opts(cookies_file, args.archive, args.output, args.store_json)

        return youtube_url, playlist_name, ydl_opts

    def build_ydl_opts(self, cookies_file, archive_file, output_location,store_json):
        ydl_opts = {

            "cookiefile": cookies_file,
            "download_archive": archive_file,
            "outtmpl": (output_location + "/%(playlist_title)s/%(playlist_index)s_%(id)s_%(title)s.%(ext)s"),
            "quiet": True,
            "ignore_errors": True,
            "writeinfojson": store_json,
            "skip_download": True,
            "verbose": False,
            }
        # if proxy:
        #     ydl_opts['yes-playlist']=True
        #     store_json = False

        print(ydl_opts)

        return ydl_opts

    def get_youtube_client(self):
        """ Log Into Youtube, Copied from Youtube Data API """
        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "youtube"
        api_version = "v3"
        client_secrets_file = "clientsecrets.json"

        # Get credentials and create an API client
        scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes)
        credentials = flow.run_console()

        # from the Youtube DATA API
        youtube_client = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials)

        return youtube_client

    def process_video_item(self, video_item, dryrun=False):
        try:
            print("track used")
            song_name = video_item["track"]
            artist = video_item["artist"]
            print(artist, song_name)
        except KeyError:
            if video_item["title"]:
                print("Parser Input", video_item["title"])
                if get_artist_title(str(video_item["title"])) is not None:
                    artist, song_name = get_artist_title(str(video_item["title"]))
                    print(artist, song_name, "parser used")
                else:
                    song_name = None
                    artist = None

                
            else:
                song_name = None
                artist = None
        # if dryun:
        #     return None
        # else:
        if song_name is not None and artist is not None:
            self.build_spotify_uris(artist, song_name)

    def youtube_dl_call(self, youtube_url, ydl_opts):

        """Call youtube-dl module"""
 

        if "playlist" in youtube_url:
            ydl_opts['yes-playlist']=True

            
        # use youtube_dl to collect the song name & artist name
        """
        Return a list with a dictionary for each video extracted.       
        """
        video_list = youtube_dl.YoutubeDL(ydl_opts).extract_info(
            youtube_url, download=True)
        dryrun = False
        try:
            for video in video_list["entries"]:
                self.process_video_item(video,dryrun)
        except KeyError as e:
            self.process_video_item(video_list,dryrun)
             
    def build_spotify_uris(self, artist, song_name):
        """Build Spotify URI Array"""

        spotify_uri = self.get_spotify_uri(artist, song_name)
        if spotify_uri is not None:
            # save all important info and skip any missing song and artist
            self.all_song_info[song_name] = {
            "youtube_url": youtube_url,
            "song_name": song_name,
            "artist": artist,

            # add the uri, easy to get song to put into playlist
            "spotify_uri": spotify_uri
            }
        print(spotify_uri)

    def create_spotify_playlist(self, playlist_name,):
        """Create A New Playlist"""
        year_month = datetime.now().strftime("%Y %m")

        request_body = json.dumps({
            "name": str(playlist_name),
            "description": "Collected from YoutubeArchiveProject" + year_month,
            "public": False
        })

        query = "https://api.spotify.com/v1/users/{}/playlists".format(
            spotify_user_id)
        response = requests.post(
            query,
            data=request_body.encode('utf-8'),
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)
            }
        )
        response_json = response.json()

        # playlist id
        return response_json["id"]

    def get_spotify_uri(self, artist, song_name):
        """Search For the Song"""
        query = "https://api.spotify.com/v1/search?query=track%3A{}+artist%3A{}&type=track&offset=0&limit=20".format(
            song_name,
            artist
        )
        response = requests.get(
            query,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)
            }
        )
        response_json = response.json()
        songs = response_json["tracks"]["items"]

        #use only first song
        if not songs: 
            return None
        else:
            uri = songs[0]['uri']
            print(uri)
            return uri

    def archive_youtube_playlist(self, youtube_url, playlist_name, ydl_opts):
        """Process Youtube Link"""
        # populate dictionary of songs from youtube link
        if playlist_name:
            playlist_name = playlist_name
        self.youtube_dl_call(youtube_url, ydl_opts)
        #if args.dryrun == False:
        self.save_to_spotify(playlist_name)

    def save_to_spotify(self, playlist_name):
        """Commit Playlist to Spotify"""
        # collect all of uri from global array.
        print(self.all_song_info.items())
        uris = [info["spotify_uri"]
                for song, info in self.all_song_info.items()]
        
        # create a new playlist
        playlist_id = self.create_spotify_playlist(playlist_name)

        # add all songs into new playlist
        request_data = json.dumps(uris)

        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(
            playlist_id)

        response = requests.post(
            query,
            data=request_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)
            }
        )

        # check for valid response status
        if response.status_code != 200:
            raise ResponseException(response.status_code)

        response_json = response.json()
        return response_json




if __name__ == '__main__':
    cp = CreatePlaylist()
    youtube_url, playlist_name, ydl_opts = cp.get_args()
    cp.archive_youtube_playlist(youtube_url, playlist_name, ydl_opts)
