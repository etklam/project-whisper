import yt_dlp
import os
import logging

def download_audio(url, output_dir="input/"):
    """Download single audio file and return local path"""
    # Ensure output directory and log file exist
    os.makedirs(output_dir, exist_ok=True)
    downloaded_file = os.path.join(output_dir, 'downloaded_urls.txt')

    downloaded_urls = set()

    # Load downloaded URLs
    if os.path.exists(downloaded_file):
        with open(downloaded_file, 'r') as f:
            downloaded_urls = set(line.strip() for line in f)

    # Skip if already downloaded
    if url in downloaded_urls:
        logging.info(f"Skipping already downloaded URL: {url}")
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
            
            logging.info(f"Successfully downloaded: {filename}")
            return filename
    except Exception as e:
        logging.error(f"Download failed: {e}")
        return None

def download_from_urls(url_file, output_dir="input/"):
    """Batch download all MP3s from URL file"""
    if not os.path.exists(url_file):
        logging.error(f"URL file does not exist: {url_file}")
        return False
    
    try:
        with open(url_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        
        success_count = 0
        for url in urls:
            if download_audio(url, output_dir):
                success_count += 1
        
        logging.info(f"Batch download complete: {success_count}/{len(urls)} URLs succeeded")
        return success_count > 0
    except Exception as e:
        logging.error(f"Batch download failed: {str(e)}")
        return False