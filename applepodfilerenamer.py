import os
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
import shutil
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
import subprocess
import re

def sanitize_filename(filename):
    # Remove or replace invalid characters
    # First, replace common problematic characters
    filename = filename.replace(':', '-')
    filename = filename.replace('/', '-')
    filename = filename.replace('\\', '-')
    filename = filename.replace('|', '-')
    filename = filename.replace('*', '-')
    filename = filename.replace('?', '-')
    filename = filename.replace('"', "'")
    filename = filename.replace('<', '-')
    filename = filename.replace('>', '-')

    # Remove any other invalid characters
    filename = re.sub(r'[^\w\s\'-\(\)\[\]\{\}_.,]', '', filename)

    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')

    # Limit length
    if len(filename) > 255:
        filename = filename[:255]

    return filename if filename else 'unnamed'

def select_directory(title_text):
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    directory = filedialog.askdirectory(
        title=title_text
    )
    return directory

def extract_aac_from_m4a(m4a_path):
    try:
        # Create output path for AAC file
        output_path = os.path.splitext(m4a_path)[0] + '.aac'

        command = [
            'ffmpeg',
            '-i', m4a_path,
            '-vn',
            '-acodec', 'copy',
            output_path
        ]

        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"Successfully extracted AAC from: {m4a_path}")
            os.remove(m4a_path)
            return output_path
        else:
            print(f"Error extracting AAC: {result.stderr}")
            return m4a_path

    except Exception as e:
        print(f"Error during AAC extraction: {str(e)}")
        return m4a_path

def get_metadata(file_path):
    file_ext = file_path.lower().split('.')[-1]

    try:
        if file_ext in ['mp3', 'aac']:
            audio = MP3(file_path)
            artist = str(audio.tags.get('TPE1', 'Unknown Artist')[0])
            album = str(audio.tags.get('TALB', 'Unknown Album')[0])
            title = str(audio.tags.get('TIT2', os.path.splitext(os.path.basename(file_path))[0])[0])
        elif file_ext == 'm4a':
            audio = MP4(file_path)
            artist = str(audio.tags.get('\xa9ART', ['Unknown Artist'])[0])
            album = str(audio.tags.get('\xa9alb', ['Unknown Album'])[0])
            title = str(audio.tags.get('\xa9nam', [os.path.splitext(os.path.basename(file_path))[0]])[0])

        return {
            'artist': sanitize_filename(artist.strip()),
            'album': sanitize_filename(album.strip()),
            'title': sanitize_filename(title.strip())
        }
    except Exception as e:
        print(f"Error reading metadata from {file_path}: {str(e)}")
        return None

def process_audio_files(source_dir, dest_dir):
    if not source_dir or not dest_dir:
        print("Source or destination directory not selected. Exiting...")
        return

    for dirpath, dirnames, filenames in os.walk(source_dir):
        for filename in filenames:
            if filename.lower().endswith(('.mp3', '.m4a')):
                file_path = os.path.join(dirpath, filename)

                metadata = get_metadata(file_path)
                if not metadata:
                    continue

                if filename.lower().endswith('.m4a'):
                    file_path = extract_aac_from_m4a(file_path)
                    if not os.path.exists(file_path):
                        continue

                # Create artist and album directories in destination
                artist_dir = os.path.join(dest_dir, metadata['artist'])
                album_dir = os.path.join(artist_dir, metadata['album'])

                # Create directories using Path object for better path handling
                Path(album_dir).mkdir(parents=True, exist_ok=True)

                # Determine new filename
                new_ext = '.aac' if file_path.lower().endswith('.aac') else os.path.splitext(file_path)[1]
                new_filename = f"{metadata['title']}{new_ext}"
                new_filepath = os.path.join(album_dir, new_filename)

                try:
                    if os.path.exists(new_filepath):
                        print(f"File already exists: {new_filepath}")
                        if os.path.normpath(file_path) != os.path.normpath(new_filepath):
                            os.remove(file_path)
                        continue

                    shutil.move(file_path, new_filepath)
                    print(f"Moved and renamed: {filename} -> {new_filepath}")
                except Exception as e:
                    print(f"Error processing {filename}: {str(e)}")

def main():
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True)
    except FileNotFoundError:
        print("Error: ffmpeg is not installed. Please install ffmpeg to use this script.")
        return

    source_dir = select_directory("Select the source directory containing your music files")
    if not source_dir:
        print("No source directory selected. Exiting...")
        return

    dest_dir = select_directory("Select the destination directory for organized music files")
    if not dest_dir:
        print("No destination directory selected. Exiting...")
        return

    process_audio_files(source_dir, dest_dir)

if __name__ == "__main__":
    main()
