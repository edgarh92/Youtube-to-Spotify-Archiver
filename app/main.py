from typing import Any
from spotify import Spotify
from youtube import Youtube
from datetime import datetime
import argparse
from app_logger import setup_logger


def build_ydl_opts(
    cookies_file: str,
    archive_file: str,
    output_location: str,
    store_json: bool
        ) -> dict[str, Any]:
        
    json_out_format = "/%(playlist_title)s/\
        %(playlist_index)s_%(id)s_%(title)s.%(ext)s"
    ydl_opts = {
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
    return ydl_opts


def url_to_id(playlist_id: str) -> str:
    """Extracts youtube id from url. 
    If url is a playlist, it will return the id only. Does nothing if already an id. 

    Args:
        url (str): Youtube URL

    Returns:
        str: Youtube ID
    """
    for char in ["list=", "list\\="]:
        if char in playlist_id:
            playlist_id = playlist_id.split(char)[1].split("\\&")[0]

    return playlist_id
    

def get_args():
    """Source arguments for CLI and returns args as tuples.

    Returns:
        youtube_url(str), playlist_name(str), ydl_opts(dict), args.dryrun(bool) : Arguments as tuples
    """    
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
        action="store_true",
        required=False,
        default=False,
        help="Do not add to Spotify.",
    )
    parser.add_argument(
        "-playlist",
        "--playlist",
        type=str,
        default=None,
        required=False,
        help="Save to specific Spotify Playlist \
            (Default: Youtube Playlist Name)",
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
    

    ydl_opts = build_ydl_opts(
        cookies_file,
        args.archive,
        args.output,
        args.store_json)

    return youtube_url, playlist_name, ydl_opts, args.dryrun


def main():
    youtube_url, playlist_name, ydl_opts, dryrun = get_args()
    sp = Spotify()
    yt = Youtube(ydl_input_ops=ydl_opts)
    archive_logger = setup_logger(__name__)
    
    yt_playlist_id = url_to_id(youtube_url)
    archive_logger.info(f'Playlist ID: {yt_playlist_id}')
    if not playlist_name:
        playlist_name = yt.get_playlist_title(yt_playlist_id)
    
    if dryrun:
        print("INFO: Dryrun")
    else:
        spotify_playlist_name = playlist_name
        spotify_playlist_id = sp.create_playlist(spotify_playlist_name)
    
    archive_logger.info(f'URL:{youtube_url}')
    songs = yt.get_songs_from_playlist(yt_playlist_id)

    for song in songs:
        song_uri = sp.get_song_uri(song.artist, song.title)

        if not song_uri:
            archive_logger.error(f"{song.artist} - {song.title} was not found!")
            continue
        
        if dryrun:
            continue
        
        was_added = sp.add_song_to_playlist(song_uri, spotify_playlist_id)

        if was_added:
            archive_logger.info(
                f'{song.artist} - {song.title} was added to playlist.')
    
    if not dryrun:
        total_songs_added = sp._num_playlist_songs(spotify_playlist_id)
        archive_logger.info(f'Added {total_songs_added} songs out of {len(songs)}')


if __name__ == "__main__":
    main()
