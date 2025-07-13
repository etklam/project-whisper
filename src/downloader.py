import yt_dlp
import os
import logging
from datetime import datetime
from .file_manager import FileManager

def download_audio(url, file_manager=None):
    """Download single audio file and return local path"""
    if file_manager is None:
        file_manager = FileManager()
    
    # 取得下載記錄檔案路徑
    downloaded_file = file_manager.get_path('data_input_urls', 'downloaded_urls.txt')
    downloaded_urls = set()

    # 載入已下載的 URLs
    if downloaded_file.exists():
        with open(downloaded_file, 'r', encoding='utf-8') as f:
            downloaded_urls = set(line.strip() for line in f)

    # 如果已下載則跳過
    if url in downloaded_urls:
        logging.info(f"跳過已下載的 URL: {url}")
        return None

    # 設定下載選項
    output_dir = file_manager.get_path('data_input_audio_raw')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f"{output_dir}/{timestamp}_%(title)s.%(ext)s",
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
            
            # 記錄已下載的 URL
            with open(downloaded_file, 'a', encoding='utf-8') as f:
                f.write(url + '\n')
            
            logging.info(f"成功下載: {filename}")
            return filename
    except Exception as e:
        logging.error(f"下載失敗: {e}")
        return None

def download_from_urls(url_file=None, file_manager=None):
    """批次下載所有 MP3 檔案"""
    if file_manager is None:
        file_manager = FileManager()
    
    # 如果沒有指定 URL 檔案，使用預設路徑
    if url_file is None:
        url_file = file_manager.get_path('data_input_urls', 'urls.txt')
    
    if not os.path.exists(url_file):
        logging.error(f"URL 檔案不存在: {url_file}")
        return False
    
    try:
        with open(url_file, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        success_count = 0
        failed_urls = []
        
        for url in urls:
            try:
                result = download_audio(url, file_manager)
                if result:
                    success_count += 1
                else:
                    failed_urls.append(url)
            except Exception as e:
                logging.error(f"下載 URL 失敗 {url}: {e}")
                failed_urls.append(url)
        
        # 記錄失敗的 URLs
        if failed_urls:
            failed_file = file_manager.get_path('data_input_urls', 'failed_urls.txt')
            with open(failed_file, 'w', encoding='utf-8') as f:
                for url in failed_urls:
                    f.write(f"{url}\n")
            logging.warning(f"失敗的 URLs 已記錄到: {failed_file}")
        
        logging.info(f"批次下載完成: {success_count}/{len(urls)} 個 URLs 成功")
        return success_count > 0
    except Exception as e:
        logging.error(f"批次下載失敗: {str(e)}")
        return False