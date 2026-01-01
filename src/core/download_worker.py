"""Download worker thread for processing individual download tasks."""
import os
import re
import subprocess
from typing import Optional
from dataclasses import dataclass

from PySide6.QtCore import QThread, Signal

from ..config.settings import AppSettings
from ..config.constants import STATUS_DOWNLOADING, STATUS_COMPLETED, STATUS_FAILED, STATUS_CANCELLED
from ..utils.logger import logger
from ..utils.validators import is_spotify_url


@dataclass
class DownloadTask:
    """Represents a single download task."""
    id: int
    url: str
    status: str = STATUS_DOWNLOADING
    progress: int = 0
    speed: str = ""
    eta: str = ""
    output_file: Optional[str] = None
    error_message: Optional[str] = None


class DownloadWorker(QThread):
    """Worker thread for downloading music from Spotify or YouTube."""
    
    # Signals
    progress_updated = Signal(int, str, str)  # progress, speed, eta
    status_changed = Signal(str)  # status message
    finished = Signal(str, str, str)  # status, output_file, error_message
    
    def __init__(self, task: DownloadTask, settings: AppSettings, parent=None):
        super().__init__(parent)
        self.task = task
        self.settings = settings
        self._should_cancel = False
        self._process: Optional[subprocess.Popen] = None
    
    def cancel(self) -> None:
        """Cancel the download."""
        self._should_cancel = True
        if self._process and self._process.poll() is None:
            try:
                self._process.terminate()
                logger.info(f"Cancelled download task {self.task.id}")
            except Exception as e:
                logger.error(f"Error cancelling task {self.task.id}: {e}")
    
    def run(self) -> None:
        """Execute the download task."""
        logger.info(f"Starting download task {self.task.id}: {self.task.url}")
        self.status_changed.emit("Preparing download...")
        
        try:
            # Ensure output directory exists
            os.makedirs(self.settings.output_dir, exist_ok=True)
            
            # Build command based on URL type or search query
            if is_spotify_url(self.task.url):
                cmd = self._build_spotify_command()
            elif self._is_youtube_search(self.task.url):
                cmd = self._build_youtube_command()
            elif self.task.url.startswith("ytsearch"):
                # yt-dlp search query
                cmd = self._build_youtube_command()
            else:
                # Assume it's a Spotify search query (song name)
                cmd = self._build_spotify_command()
            
            logger.debug(f"Command: {' '.join(cmd)}")
            
            # Execute download
            success, output_file, error_msg = self._execute_command(cmd)
            
            if self._should_cancel:
                self.finished.emit(STATUS_CANCELLED, "", "Download cancelled by user")
                return
            
            if success:
                logger.info(f"Task {self.task.id} completed successfully")
                self.finished.emit(STATUS_COMPLETED, output_file or "", "")
            else:
                logger.error(f"Task {self.task.id} failed: {error_msg}")
                self.finished.emit(STATUS_FAILED, "", error_msg or "Download failed")
        
        except Exception as e:
            logger.exception(f"Exception in download task {self.task.id}")
            self.finished.emit(STATUS_FAILED, "", str(e))
    
    def _build_spotify_command(self) -> list[str]:
        """Build command for Spotify download using spotdl."""
        cmd = [
            self.settings.spotdl_path,
            "download",
            self.task.url,
            "--output", self.settings.output_dir,
        ]
        
        # Add format if not mp3 (mp3 is default)
        if self.settings.default_format.lower() != "mp3":
            cmd.extend(["--format", self.settings.default_format])
        
        # Add bitrate if not "Best"
        if self.settings.default_quality != "Best":
            bitrate = self.settings.default_quality.replace("kbps", "k")
            cmd.extend(["--bitrate", bitrate])
        
        return cmd
    
    def _build_youtube_command(self) -> list[str]:
        """Build command for YouTube download using yt-dlp."""
        output_template = os.path.join(
            self.settings.output_dir,
            "%(title)s.%(ext)s"
        )
        
        cmd = [
            self.settings.yt_dlp_path,
            "-f", "ba",  # best audio
            "-x",  # extract audio
            "--audio-format", self.settings.default_format,
            "-o", output_template,
        ]
        
        # Add quality settings
        if self.settings.default_quality == "Best":
            cmd.extend(["--audio-quality", "0"])  # best VBR
        else:
            bitrate = self.settings.default_quality.replace("kbps", "k")
            cmd.extend(["--audio-quality", bitrate])
        
        # Add metadata options
        if self.settings.embed_metadata:
            cmd.append("--add-metadata")
        
        if self.settings.embed_thumbnail:
            cmd.append("--embed-thumbnail")
        
        # Add the URL or search query
        cmd.append(self.task.url)
        
        return cmd
    
    def _is_youtube_search(self, text: str) -> bool:
        """Check if text is a YouTube URL or search query."""
        from ..utils.validators import is_youtube_url
        return is_youtube_url(text) or text.startswith("ytsearch")
    
    def _execute_command(self, cmd: list[str]) -> tuple[bool, Optional[str], Optional[str]]:
        """
        Execute download command and parse output.
        
        Returns:
            (success, output_file, error_message)
        """
        try:
            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
        except FileNotFoundError:
            return (False, None, f"Command not found: {cmd[0]}")
        except Exception as e:
            return (False, None, f"Failed to start process: {str(e)}")
        
        output_lines = []
        output_file = None
        last_progress = 0
        
        while True:
            if self._should_cancel:
                if self._process.poll() is None:
                    self._process.terminate()
                return (False, None, "Cancelled by user")
            
            line = self._process.stdout.readline() if self._process.stdout else ""
            
            if not line:
                if self._process.poll() is not None:
                    break
                continue
            
            output_lines.append(line)
            logger.debug(f"Task {self.task.id}: {line.rstrip()}")
            
            # Parse progress
            progress, speed, eta = self._parse_progress(line, last_progress)
            if progress != last_progress:
                last_progress = progress
                self.progress_updated.emit(progress, speed, eta)
            
            # Try to extract output filename
            if not output_file:
                file_match = re.search(r'\[download\] Destination: (.+)', line)
                if file_match:
                    output_file = file_match.group(1).strip()
                else:
                    # spotdl format
                    file_match = re.search(r'Downloaded "(.+)"', line)
                    if file_match:
                        output_file = file_match.group(1).strip()
        
        returncode = self._process.poll()
        
        if returncode == 0:
            self.progress_updated.emit(100, "", "")
            return (True, output_file, None)
        else:
            error_text = "\n".join(output_lines[-20:])  # Last 20 lines
            return (False, output_file, error_text)
    
    def _parse_progress(self, line: str, current: int) -> tuple[int, str, str]:
        """
        Parse progress information from output line.
        
        Returns:
            (progress, speed, eta)
        """
        # yt-dlp progress format: "[download]  45.2% of 3.24MiB at 1.23MiB/s ETA 00:02"
        progress_match = re.search(r'(\d+\.?\d*)%', line)
        if progress_match:
            try:
                progress = int(float(progress_match.group(1)))
                progress = max(current, min(100, progress))
                
                # Extract speed
                speed = ""
                speed_match = re.search(r'at\s+([\d.]+\s*[KMG]?i?B/s)', line)
                if speed_match:
                    speed = speed_match.group(1)
                
                # Extract ETA
                eta = ""
                eta_match = re.search(r'ETA\s+([\d:]+)', line)
                if eta_match:
                    eta = eta_match.group(1)
                
                return (progress, speed, eta)
            except ValueError:
                pass
        
        # spotdl progress (less detailed)
        if "Downloading" in line and current < 50:
            return (50, "", "")
        if "Converting" in line and current < 80:
            return (80, "", "")
        if "Downloaded" in line and current < 100:
            return (100, "", "")
        
        return (current, "", "")
