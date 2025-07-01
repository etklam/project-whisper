import yt_dlp
import os

def download_audio(url, output_dir="output/audio"):
    """下载音频文件并返回本地路径"""
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 配置下载选项
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
        print(f"下载失败: {e}")
        return None