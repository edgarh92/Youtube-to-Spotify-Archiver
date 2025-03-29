import argparse
from dotenv import load_dotenv
from tools.app_logger import setup_logger
from tools.spotify import Spotify
from tools.youtube import Youtube
from datetime import datetime
from typing import Any


# Load the environment variables from the .env file (if present)
load_dotenv()


def build_ydl_opts(
    cookies_file: str, archive_file: str, output_location: str, store_json: bool
) -> dict[str, Any]:
    """
    Build youtube-dl options dictionary.

    Args:
        cookies_file (str): Path to cookies file.
        archive_file (str): Path to archive file.
        output_location (str): Directory to save output files.
        store_json (bool): Flag to store JSON metadata.

    Returns:
        dict[str, Any]: Dictionary of youtube-dl options.
    """
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
        "logtostderr": False,
    }
    return ydl_opts


def url_to_id(playlist_id: str) -> str:
    """
    Extract YouTube ID from URL.

    Args:
        playlist_id (str): YouTube playlist URL or ID.

    Returns:
        str: Extracted YouTube ID.
    """
    for char in ["list=", "list\\="]:
        if char in playlist_id:
            playlist_id = playlist_id.split(char)[1].split("\\&")[0]

    return playlist_id


def get_args():
    """
    Parse command-line arguments.

    Returns:
        tuple: Parsed arguments including YouTube URL, playlist name, youtube-dl options, and dry run flag.
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
        "--store_json", action="store_true", help="Download json the video."
    )

    parser.add_argument(
        "--archive",
        "--a",
        type=str,
        required=False,
        default="~/Music/JSON/archive.log",
        help="Location of archive reference file",
    )
    parser.add_argument("--cookies", type=str, required=False, help="Cookies file")
    parser.add_argument(
        "--loglevel",
        type=str,
        default="INFO",
        help="Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )

    args = parser.parse_args()
    youtube_url = args.url
    cookies_file = args.cookies
    playlist_name = args.playlist

    ydl_opts = build_ydl_opts(cookies_file, args.archive, args.output, args.store_json)

    return youtube_url, playlist_name, ydl_opts, args.dryrun


def main():
    """
    Main function to archive YouTube playlist to Spotify.

    Steps:
    1. Parse command-line arguments.
    2. Setup logger.
    3. Initialize Spotify and YouTube tools.
    4. Extract playlist ID from URL.
    5. Retrieve songs from YouTube playlist.
    6. Add songs to Spotify playlist (if not in dry run mode).
    """

    # Setup required variables
    youtube_url, playlist_name, ydl_opts, dryrun = get_args()
    import logging

    loglevel = logging.getLevelName(ydl_opts.pop("loglevel", "INFO"))
    archive_logger = setup_logger(__name__, level=loglevel)
    sp = Spotify()
    yt = Youtube(ydl_input_ops=ydl_opts)

    # Get the YouTube playlist details
    yt_playlist_id = url_to_id(youtube_url)
    archive_logger.info(f"Playlist ID: {yt_playlist_id}")
    if not playlist_name:
        playlist_name = yt.get_playlist_title(yt_playlist_id)

    playlist_description = yt.get_playlist_description(yt_playlist_id)
    if not playlist_description:
        playlist_description = f"YouTube playlist imported on {datetime.now().strftime('%Y-%m-%d')}"

    # Retrieve music information from the YouTube playlist
    archive_logger.info(f"URL:{youtube_url}")
    songs = yt.get_songs_from_playlist(yt_playlist_id)
    archive_logger.debug(
        "Starting main process with loglevel set to " + logging.getLevelName(loglevel)
    )

    # Add the retrieved songs to the Spotify playlist
    if dryrun:
        archive_logger.info("Dryrun mode enabled. No songs will be added to Spotify.")
    else:
        archive_logger.info("Creating Spotify playlist.")
        spotify_playlist_id = sp.create_playlist(playlist_name, playlist_description)

    for song in songs:
        song_uri = sp.get_song_uri(song.artist, song.title)

        if not song_uri:
            archive_logger.error(f"{song.artist} - {song.title} was not found!")
            continue

        if dryrun:
            continue
        was_added = sp.add_song_to_playlist(song_uri, spotify_playlist_id)

        if was_added:
            archive_logger.info(f"{song.artist} - {song.title} was added to playlist.")

    if not dryrun:
        total_songs_added = sp._num_playlist_songs(spotify_playlist_id)
        archive_logger.info(f"Added {total_songs_added} songs out of {len(songs)}")


if __name__ == "__main__":
    main()
