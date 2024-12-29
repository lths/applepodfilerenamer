# Music Library Organizer

A Python script that organizes your music library by automatically sorting MP3 and M4A files into artist/album folders based on their metadata. It can also extract AAC audio from M4A files.

## Features

- Organizes music files into Artist/Album folder structure
- Extracts AAC from M4A files (requires FFmpeg)
- Reads and uses metadata for organization
- Handles special characters in filenames
- GUI directory selection
- Maintains original metadata
- Supports both MP3 and M4A formats

## Prerequisites

- Python 3.6 or higher
- FFmpeg installed and in system PATH
- Required Python packages:
  - mutagen
  - tkinter (usually comes with Python)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/music-library-organizer.git
