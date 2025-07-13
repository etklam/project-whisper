import os
import logging
from pathlib import Path
from .file_manager import FileManager

def clean_directory(directory=None, keep_extensions=None, file_manager=None):
    """清理目錄中不符合指定副檔名的檔案
    
    Args:
        directory (str): 要清理的目錄路徑，如果為 None 則清理舊的 input 目錄
        keep_extensions (list): 要保留的副檔名列表 (例如 ['.md'])
        file_manager (FileManager): 檔案管理器實例
    """
    # 配置日誌
    logger = logging.getLogger("cleaner")
    
    if file_manager is None:
        file_manager = FileManager()
    
    # 如果沒有指定目錄，清理舊的 input 目錄
    if directory is None:
        directory = "input"
    
    directory_path = Path(directory)
    
    # 確保目錄存在
    if not directory_path.exists():
        logger.error(f"目錄不存在: {directory}")
        return False
    
    # 預設保留 .md 檔案
    if keep_extensions is None:
        keep_extensions = ['.md', '.txt']
    
    try:
        # 遍歷所有檔案
        files_deleted = 0
        files_moved = 0
        
        for file_path in directory_path.rglob('*'):
            # 跳過目錄
            if file_path.is_dir():
                continue
            
            # 檢查檔案副檔名是否應該保留
            if file_path.suffix.lower() in keep_extensions:
                logger.info(f"保留檔案: {file_path}")
                continue
            
            # 特殊處理：移動音訊檔案到新結構
            if file_path.suffix.lower() in ['.mp3', '.wav', '.m4a', '.flac']:
                try:
                    new_path = file_manager.move_file(
                        file_path, 'data_input_audio_raw', file_path.name
                    )
                    logger.info(f"音訊檔案已移動: {file_path} -> {new_path}")
                    files_moved += 1
                    continue
                except Exception as e:
                    logger.error(f"移動音訊檔案失敗 {file_path}: {e}")
            
            # 刪除其他檔案
            try:
                file_path.unlink()
                logger.info(f"已刪除: {file_path}")
                files_deleted += 1
                
            except Exception as e:
                logger.error(f"刪除檔案失敗 {file_path}: {e}")
        
        logger.info(f"清理完成: 刪除 {files_deleted} 個檔案，移動 {files_moved} 個檔案")
        return True
        
    except Exception as e:
        logger.error(f"清理目錄時發生錯誤: {e}")
        return False

def clean_temp_files(file_manager=None, older_than_hours=24):
    """清理暫存檔案
    
    Args:
        file_manager (FileManager): 檔案管理器實例
        older_than_hours (int): 清理多少小時前的檔案
    """
    logger = logging.getLogger("cleaner")
    
    if file_manager is None:
        file_manager = FileManager()
    
    try:
        cleaned_count = file_manager.clean_temp_files(older_than_hours)
        logger.info(f"暫存檔案清理完成: 清理了 {cleaned_count} 個檔案")
        return cleaned_count
    except Exception as e:
        logger.error(f"清理暫存檔案失敗: {e}")
        return 0

def archive_old_files(file_manager=None, days_old=30):
    """歸檔舊檔案
    
    Args:
        file_manager (FileManager): 檔案管理器實例
        days_old (int): 歸檔多少天前的檔案
    """
    logger = logging.getLogger("cleaner")
    
    if file_manager is None:
        file_manager = FileManager()
    
    import time
    from datetime import datetime, timedelta
    
    cutoff_date = datetime.now() - timedelta(days=days_old)
    cutoff_timestamp = cutoff_date.timestamp()
    
    archived_count = 0
    
    # 歸檔舊的轉錄檔案
    try:
        transcripts_dir = file_manager.get_path('data_output_transcripts_raw')
        for file_path in transcripts_dir.glob('*.txt'):
            if file_path.stat().st_mtime < cutoff_timestamp:
                archive_path = file_manager.get_path('data_output_reports') / 'archived' / 'transcripts'
                archive_path.mkdir(parents=True, exist_ok=True)
                
                new_path = archive_path / file_path.name
                file_path.rename(new_path)
                archived_count += 1
                logger.info(f"已歸檔轉錄檔案: {file_path} -> {new_path}")
        
        logger.info(f"檔案歸檔完成: 歸檔了 {archived_count} 個檔案")
        return archived_count
        
    except Exception as e:
        logger.error(f"歸檔檔案失敗: {e}")
        return 0

# Test code
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python cleaner.py <directory> [keep_extensions]")
        sys.exit(1)
    
    dir_path = sys.argv[1]
    extensions = sys.argv[2].split(',') if len(sys.argv) > 2 else None
    clean_directory(dir_path, extensions)