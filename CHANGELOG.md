# Changelog

## Version 2.0.0 - Latest Updates

### Fixed
- **Spotify Downloads**: Fixed spotdl command format by adding the `download` subcommand
- **Bitrate Format**: Corrected bitrate argument format (e.g., "320k" instead of "320")
- **Command Structure**: Simplified spotdl commands and removed problematic flags

### Added
- **Query Type Selector**: Added dropdown with 5 modes for better UX
  - **Auto**: Automatically detects URL type or defaults to YouTube search
  - **Spotify URL/Search**: Handles Spotify URLs or searches Spotify by song name
  - **YouTube URL**: Only accepts valid YouTube URLs
  - **Search on YouTube**: Searches YouTube for songs by name
  - **Search on Spotify**: Searches Spotify for songs by name

### Improved
- **Dynamic Placeholder**: Input field placeholder changes based on selected mode
- **Search Support**: Can now search for songs by name, not just URLs
- **Better URL Handling**: Improved logic for processing URLs vs search queries

### Technical Changes
- Updated `download_worker.py`:
  - Added `download` subcommand to spotdl
  - Fixed bitrate format for both spotdl and yt-dlp
  - Added search query detection logic
  - Simplified command building

- Updated `main_window.py`:
  - Added mode selector combo box
  - Implemented `_process_query()` method to handle different modes
  - Added dynamic placeholder updates
  - Improved query validation

## Usage Examples

### Download from URL
1. Paste Spotify or YouTube URL
2. Select quality and format
3. Click "Add to Queue"

### Search for Songs
1. Select mode: "Search on Spotify" or "Search on YouTube"
2. Type song name (e.g., "Imagine Dragons Believer")
3. Click "Add to Queue"

### Auto Mode (Default)
- Paste URL → Downloads from that source
- Type song name → Searches YouTube by default
