# YouTube to Spotify Archiver

A simple script to add all songs from a YouTube playlist to a Spotify playlist.

Works only for **Public** or **Unlisted** YouTube playlists.

## Example
![Example Run](imgs/examplerun.gif)

## What's New?
- **Faster**: Uses YouTube API to get song info instead of Selenium.
- **Convenient**: No need to refresh token after every hour.
- **Reliable**: Adds 85-95% of the songs from popular YouTube playlists.

## Stats
Added 142 songs to Spotify playlist out of 150 songs from YouTube playlist.

## Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Spotify Developer Account
- YouTube API Key

### Spotify Developer Setup

1. **Create an app:** [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications)

    ![Setup](imgs/setup.png)

2. **Copy the Client ID and Client Secret:**

    ![Copy](imgs/copy.png)

3. **Set redirect URI to `http://localhost:8888/callback`:**

    ![Redirect URI](imgs/redirecturi.png)

### Get YouTube API Key

[Instructions for creating a YouTube API key](getkey.md)

### Environment Setup

1. **Clone the repository:**

    ```sh
    git clone https://github.com/edgarh92/Youtube-to-Spotify-Archiver.git
    cd Youtube-to-Spotify-Archiver
    ```

2. **Install dependencies:**

    ```sh
    pip install -r requirements.txt
    ```

3. **Set up environment variables:**

    Create a `.env` file in the root directory and add the following variables:

    ```env
    SPOTIFY_USER_ID=<your_user_id>
    SPOTIFY_CLIENT_ID=<your_spotify_client_id>
    SPOTIFY_CLIENT_SECRET=<your_spotify_client_secret>
    SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
    YOUTUBE_API_KEY=<your_youtube_api_key>
    ```
    Replace the `<fields>` with the values you retrieved when setting up your Spotify Application and YouTube API key.

    Spotify user id can be obtained from the "Username" field under [Profile](https://www.spotify.com/us/account/profile/).


## Usage

```sh
python app/main.py -u "https://www.youtube.com/playlist?list=#######"
```

### CLI Arguments

- `--url`, `-u`: Link to Video or Song URL (required)
- `-o`, `--output`: Destination location of JSON files (default: `~/Music/JSON`)
- `--dryrun`: Do not add to Spotify
- `-playlist`, `--playlist`: Save to specific Spotify Playlist (default: YouTube Playlist Name)
- `--store_json`: Download JSON metadata of the video.
- `--archive`, `--a`: Location of archive reference file (default: `~/Music/JSON/archive.log`)
- `--cookies`: Path to cookies file
- `--loglevel`: Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

## Logs
Logs are output to `./logs/youtube.log`.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License.
