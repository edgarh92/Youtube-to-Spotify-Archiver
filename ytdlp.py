

import yt_dlp


class VideoTitleExtractor:

    def __init__(self):
        self.videoinfo = ""

    def process_video_track(self, video_item) -> tuple:
        '''Process a dictionary of metadata and return None or song_name, artist'''
        try:
            song_name = video_item["track"]
            artist = video_item["artist"]
            return str(artist), str(song_name)
           
        except KeyError as EmptyValue:
            return None, None

    def call_yt_dlp(self, video_id, ydl_opts) -> dict:
        ydl_opts = ydl_opts

        youtube_url = "https://www.youtube.com/watch?v=" + video_id
        video_info = yt_dlp.YoutubeDL(ydl_opts).extract_info(
                        youtube_url, download=True)
        return video_info


