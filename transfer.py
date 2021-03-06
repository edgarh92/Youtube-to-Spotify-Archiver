from spotify import Spotify
from youtube import Youtube
from datetime import datetime
import argparse
from logger import setup_logger

def build_ydl_opts(cookies_file, archive_file, output_location,store_json):
    json_out_format = "/%(playlist_title)s/%(playlist_index)s_%(id)s_%(title)s.%(ext)s"
    ydl_opts = {
        "cookiefile": cookies_file,
        "download_archive": archive_file,
        "outtmpl": (output_location + json_out_format),
        "quiet": True,
        "ignore_errors": True,
        "writeinfojson": store_json,
        "skip_download": True,
        "verbose": False,
        }
    return ydl_opts

def get_args():
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
            "--cookies",
            type=str,
            required=True,
            help="Cookies file"
        )

        args = parser.parse_args()
        youtube_url = args.url
        cookies_file = args.cookies
        playlist_name = args.playlist

        ydl_opts = build_ydl_opts(cookies_file, args.archive, args.output, args.store_json)

        return youtube_url, playlist_name, ydl_opts

def main():
    sp = Spotify()
    yt = Youtube()
    youtube_url, playlist_name, ydl_opts = get_args()
    archive_logger = setup_logger(__name__)
    

    yt_playlist_id = youtube_url
    spotify_playlist_name = playlist_name
    spotify_playlist_id = sp.create_playlist(spotify_playlist_name)
    archive_logger.info(f'URL:{youtube_url}')
    
    songs = yt.get_songs_from_playlist(yt_playlist_id, ydl_opts)

    for song in songs:
        song_uri = sp.get_song_uri(song.artist, song.title)

        if not song_uri:
            archive_logger.error(f"{song.artist} - {song.title} was not found!")
            continue
        
        was_added = sp.add_song_to_playlist(song_uri, spotify_playlist_id)

        if was_added:
            archive_logger.info(f'{song.artist} - {song.title} was added to playlist.')

    total_songs_added = sp._num_playlist_songs(spotify_playlist_id)
    archive_logger.info(f'Added {total_songs_added} songs out of {len(songs)}')

if __name__ == "__main__":
    main()
