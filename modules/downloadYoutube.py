import yt_dlp


class Youtube:
    def __init__(
        self,
        executor,
        showMessage,
        on_tasks_started=None,
        on_task_completed=None,
    ):
        self.executor = executor
        self.showMessage = showMessage
        self.on_tasks_started = on_tasks_started
        self.on_task_completed = on_task_completed

    # playlist check
    def isPlaylist(self, url):
        """Check if the URL is a single video or a playlist using yt-dlp."""
        ydl_opts = {"quiet": True}

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(
                url, download=False
            )  # Fetch metadata without downloading

        # 'entries' key exists if it's a playlist (contains multiple videos)
        return "entries" in info

    # youtube songs downloader
    def download(self, url, output_folder):

        # self.showMessage("Debug", "Inside Youtube.download", "i")

        import os

        try:
            # output folder check
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            # playlist check
            if self.isPlaylist(url):
                self.downloadPlaylist(url, output_folder)
            else:
                # Single video => one task
                if self.on_tasks_started:
                    self.on_tasks_started(1)
                self.executor.submit(self._downloadSong_with_progress, url, output_folder)
        except Exception as e:
            error_message = f"Failed to start download: {url}\nError: {str(e)}"
            self.showMessage("Download Error", error_message, "e")

    # download playlist
    def downloadPlaylist(self, playlist_url, output_folder):
        # Download all videos mp3 in a playlist using multiple threads.
        try:
            ydl_opts = {
                "quiet": True,
                "extract_flat": True,
                "force_generic_extractor": True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(playlist_url, download=False)

            video_urls = [entry["url"] for entry in info["entries"] if "url" in entry]

            # Notify UI of total number of items in playlist
            if self.on_tasks_started and video_urls:
                self.on_tasks_started(len(video_urls))

            for url in video_urls:
                self.executor.submit(self._downloadSong_with_progress, url, output_folder)
        except Exception as e:
            warning_message = (
                f"Failed to process playlist: {playlist_url}\nError: {str(e)}"
            )
            self.showMessage("Playlist Download Error", warning_message, "w")

    def _downloadSong_with_progress(self, Song_url, output_folder):
        """Wrapper around downloadSong that also updates task progress."""
        try:
            self.downloadSong(Song_url, output_folder)
        finally:
            if self.on_task_completed:
                self.on_task_completed()

    # download song
    def downloadSong(self, Song_url, output_folder):

        # self.showMessage("Debug", "Inside Youtube.downloadSong", "i")

        # yt-dlp options for high-quality MP3 conversion
        try:

            # self.showMessage("Debug", "Running Ytdlp command", "i")

            ydl_opts = {
                "format": "bestaudio/best",
                "extractaudio": True,  # Extract only the audio
                "audioformat": "mp3",  # Convert to MP3
                "outtmpl": f"{output_folder}/%(title)s.%(ext)s",  # Save with video title
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "320",  # High quality 320kbps
                    }
                ],
                "ffmpeg_args": ["-b:a", "320k", "-ar", "44100", "-ac", "2"],
                "keepvideo": False,  # Don't keep the original video file
                "writesubtitles": False,  # Don't download subtitles
                "writeautomaticsub": False,  # Don't download automatic subtitles
                "noplaylist": False,  # Allow playlist downloads
                "quiet": True,  # Reduce output noise
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                song_info = ydl.extract_info(
                    Song_url, download=True
                )  # Extract metadata
                song_title = song_info.get("title", "Unknown Song")  # Get song title

            print(f"✅ Downloaded Youtube Song: {song_title}")
            success_message = f"Downloaded: {song_title}"
            self.showMessage("Download Complete", success_message, "i")
        except Exception as e:
            error_message = f"Failed to download song: {Song_url}\nError: {str(e)}"
            self.showMessage("Song Download Error", error_message, "e")
