import yt_dlp
import os

import os
import yt_dlp

def download_audio(url, output_dir="output/audio"):
    """Download audio file and return local path"""
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Check if URL already downloaded
    downloaded_file = os.path.join(output_dir, 'downloaded_urls.txt')
    downloaded_urls = set()
    
    # Load existing downloaded URLs
    if os.path.exists(downloaded_file):
        with open(downloaded_file, 'r') as f:
            downloaded_urls = set(line.strip() for line in f)
    
    # Skip if already downloaded
    if url in downloaded_urls:
        print(f"Skipping already downloaded URL: {url}")
        return None
    
    # Configure download options
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f"{output_dir}/%(title)s.%(ext)s",
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')
            
            # Record downloaded URL
            with open(downloaded_file, 'a') as f:
                f.write(url + '\n')
            
            return filename
    except Exception as e:
        print(f"Download failed: {e}")
        return None