import yt_dlp
import os

def download_audio(url, output_dir="output/audio"):
    """Download audio file and return local path"""
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
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
            return ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')
    except Exception as e:
        print(f"Download failed: {e}")
        return None