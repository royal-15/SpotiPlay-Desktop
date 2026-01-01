# SpotiPlay v2.0 - Modern Music Downloader

A completely redesigned desktop application for downloading music from Spotify and YouTube. Built with PySide6 (Qt6), SpotiPlay v2.0 features a modern Material Design-inspired interface, advanced queue management, and professional-grade download capabilities.

## ✨ Key Features

### Download Management
-   🎵 **Multi-source Support**: Download from Spotify (tracks, albums, playlists) and YouTube (videos, playlists)
-   📋 **Queue System**: Add multiple downloads and manage them efficiently
-   ⚡ **Parallel Downloads**: Configure up to 10 simultaneous downloads
-   📊 **Real-time Progress**: See download progress, speed, and ETA for each task
-   🔄 **Smart Auto-start**: Downloads begin automatically when added to queue

### Modern Interface
-   🎨 **Material Design**: Clean, modern interface with Spotify green accents
-   🌙 **Dark Theme**: Eye-friendly dark theme by default
-   🪟 **Responsive Layout**: Resizable window (minimum 900x600)
-   📢 **Toast Notifications**: Non-intrusive notifications for important events
-   📈 **Live Statistics**: Track total, downloading, completed, and failed downloads

### Quality & Format Options
-   🎚️ **Quality Presets**: Best, 320kbps, 256kbps, 192kbps, 128kbps
-   🎼 **Format Selection**: MP3, M4A, FLAC, WAV
-   🖼️ **Metadata Embedding**: Automatic title, artist, album, and cover art
-   ⚙️ **Configurable Tools**: Custom paths for yt-dlp, spotdl, and FFmpeg

## 🚀 Installation

### Prerequisites

-   **Python 3.10 or later**
-   **yt-dlp**: YouTube downloader (`pip install yt-dlp` or download from [yt-dlp releases](https://github.com/yt-dlp/yt-dlp/releases))
-   **spotdl**: Spotify downloader (`pip install spotdl`)
-   **FFmpeg**: Audio processing (download from [ffmpeg.org](https://ffmpeg.org/download.html))

### Quick Start

1. **Clone or download the repository:**
```bash
git clone https://github.com/yourusername/SpotiPlay-Desktop.git
cd SpotiPlay-Desktop
```

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

3. **Install download tools:**
```bash
# Install yt-dlp and spotdl
pip install yt-dlp spotdl

# FFmpeg (Windows): Download from ffmpeg.org and add to PATH
# Or place ffmpeg.exe in the project directory
```

4. **Run the application:**
```bash
python run.py
```

## 💻 Usage

1. **Launch the application**
   ```bash
   python run.py
   ```

2. **Configure settings** (first time)
   - Accept the disclaimer
   - Select your preferred output directory
   - Choose default quality and format

3. **Add downloads**
   - Paste a Spotify or YouTube URL in the input field
   - Or paste multiple URLs (separated by newlines)
   - Click "Add to Queue" or press Enter

4. **Manage queue**
   - Downloads start automatically
   - Monitor progress in real-time
   - Use "Cancel All" to stop downloads
   - Use "Clear Completed" to clean up the queue

5. **Access settings**
   - Click the "⚙ Settings" button
   - Configure parallel downloads (1-10)
   - Set custom tool paths if needed

### Supported URLs

**Spotify:**
- Individual tracks: `https://open.spotify.com/track/...`
- Albums: `https://open.spotify.com/album/...`
- Playlists: `https://open.spotify.com/playlist/...`

**YouTube:**
- Videos: `https://www.youtube.com/watch?v=...`
- Short links: `https://youtu.be/...`
- Playlists: `https://www.youtube.com/playlist?list=...`

## 🏗️ Project Structure

```
SpotiPlay-Desktop/
├── src/
│   ├── config/              # Configuration and constants
│   │   ├── constants.py
│   │   └── settings.py
│   ├── core/                # Download engine
│   │   ├── download_manager.py
│   │   ├── download_worker.py
│   │   └── url_parser.py
│   ├── ui/                  # User interface
│   │   ├── components/
│   │   │   └── toast.py
│   │   ├── styles/
│   │   │   └── theme.py
│   │   └── main_window.py
│   ├── utils/               # Utilities
│   │   ├── logger.py
│   │   └── validators.py
│   └── main.py              # Entry point
├── resources/               # Icons and assets
├── requirements.txt
├── run.py                   # Launcher script
└── README.md
```

## 🚀 Tech Stack

- **Framework**: [PySide6](https://doc.qt.io/qtforpython-6/) (Qt6 for Python)
- **Download Tools**: [yt-dlp](https://github.com/yt-dlp/yt-dlp), [spotdl](https://github.com/spotDL/spotify-downloader)
- **Audio Processing**: [FFmpeg](https://ffmpeg.org/)
- **Metadata**: [Mutagen](https://mutagen.readthedocs.io/)

## 👏 Acknowledgments

-   [PySide6](https://doc.qt.io/qtforpython-6/) for the modern, native-looking UI framework
-   [spotdl](https://github.com/spotDL/spotify-downloader) for Spotify download functionality
-   [yt-dlp](https://github.com/yt-dlp/yt-dlp) for YouTube download functionality
-   [FFmpeg](https://ffmpeg.org/) for audio conversion and processing

## 📦 Building Executable

To create a standalone executable:

```bash
pip install pyinstaller
pyinstaller --name="SpotiPlay" --windowed --onefile \
            --add-data="src:src" \
            --add-data="resources:resources" \
            --hidden-import=PySide6 \
            run.py
```

## ⚠️ Disclaimer

This application is for **educational purposes only**. Users are responsible for ensuring they have the legal right to download any content. Downloading copyrighted material without permission may violate copyright laws and terms of service.

## 📝 License

This project is provided as-is for educational purposes.

---

**Version**: 2.0.0  
**Author**: SpotiPlay Team  
**Built with** ❤️ **using Python and Qt**
