import sys
import subprocess
from mutagen.mp3 import MP3
from concurrent.futures import ThreadPoolExecutor


class Spotify:
    def __init__(
        self,
        executor: ThreadPoolExecutor,
        showMessage,
        on_tasks_started=None,
        on_task_completed=None,
    ):
        self.executor = executor
        self.showMessage = showMessage
        self.on_tasks_started = on_tasks_started
        self.on_task_completed = on_task_completed

    def download(self, url, download_folder):

        # self.showMessage("Debug", "Inside Spotify.download", "i")

        # Notify UI that a new task has started
        if self.on_tasks_started:
            self.on_tasks_started(1)

        try:
            # self.showMessage("Debug", "Running Spotdl command", "i")

            # Run the spotdl command to download the song
            result = subprocess.run(
                [
                    "PortablePython\\python.exe",
                    "-m",
                    "spotdl",
                    "download",
                    url,
                    "--output",
                    download_folder,
                    "--format",
                    "mp3",
                    "--bitrate",
                    "320k",
                ],
                check=True,
                capture_output=True,
                text=True,
                creationflags=(
                    subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                ),
            )

            # self.showMessage("Debug", f"{result.stdout}", "i")

            self.showMessage(
                "Download Complete", f"Downloaded {url} to {download_folder}", "i"
            )

            print(f"✅ Downloaded: {url} in {download_folder}")
        except subprocess.CalledProcessError as e:
            stderr = e.stderr.strip() if e.stderr else str(e)
            error_message = f"❌ Failed to download: {url}\nError: {stderr}"
            self.showMessage("Download Error", error_message, "e")
        except Exception as e:
            self.showMessage("Error", f"An unexpected error occurred: {str(e)}", "e")
        finally:
            # Always notify completion so UI progress stays in sync
            if self.on_task_completed:
                self.on_task_completed()

    def isFileIncomplete(self, file_path):
        # Check if an MP3 file is incomplete by verifying its metadata.
        try:
            audio = MP3(file_path)  # Load metadata
            if (
                audio.info.length < 30
            ):  # Example: Songs shorter than 30 sec are considered incomplete
                return True
        except Exception:  # If MP3 metadata can't be read, assume it's corrupted
            return True
        return False

    def retryDownloads(self, path):
        # Retry downloading incomplete MP3 files in the folder.
        print("🔍 Checking for incomplete downloads...")

        import os

        incomplete_files = []
        for file_name in os.listdir(path):
            if file_name.endswith(".mp3"):
                file_path = os.path.join(path, file_name)

                # Check if the file is incomplete
                if self.isFileIncomplete(file_path):
                    incomplete_files.append(file_name)

        # Notify UI about how many retries we are going to perform
        if self.on_tasks_started and incomplete_files:
            self.on_tasks_started(len(incomplete_files))

        for file_name in incomplete_files:
            print(
                f"⚠️ Incomplete file detected: {file_name} — Retrying download..."
            )

            # Extract song name (assuming it's in the filename)
            song_name = os.path.splitext(file_name)[0]

            try:
                # Re-download using spotdl
                subprocess.run(
                    [
                        "spotdl",
                        "download",
                        song_name,
                        "--output",
                        path,
                    ],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=(
                        subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
                    ),
                )
                print(f"✅ Successfully re-downloaded: {file_name}")
            except subprocess.CalledProcessError:
                error_message = f"Failed to re-download: {file_name}"
                self.showMessage("Re-download Error", error_message, "e")
            finally:
                if self.on_task_completed:
                    self.on_task_completed()
