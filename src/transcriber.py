import torch
import whisper
from whisper.utils import get_writer
import sys
import configparser
import os
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from .file_manager import FileManager

def transcribe_audio(input_path: str, file_manager=None, model_name: str = None):
    """轉錄音訊檔案為文字"""
    # 配置日誌
    logger = logging.getLogger("transcriber")
    
    if file_manager is None:
        file_manager = FileManager()
    
    # 讀取配置檔案
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    # 使用配置預設值
    if model_name is None:
        model_name = config.get('transcriber', 'model_name', fallback='base')
    
    # 檢查 ROCm 可用性
    if not torch.cuda.is_available():
        logger.info("ROCm 不可用，使用 CPU")
    else:
        logger.info(f"使用 GPU: {torch.cuda.get_device_name(0)}")

    # 處理路徑相容性
    input_path = Path(input_path)
    if not input_path.exists():
        logger.error(f"輸入檔案不存在: {input_path}")
        return None
    
    try:
        # 嘗試載入模型
        model = whisper.load_model(model_name)
    except RuntimeError as e:
        if "Model" in str(e) and "not found" in str(e):
            logger.info(f"模型 {model_name} 未找到，正在下載...")
            # 自動下載模型
            subprocess.run(["whisper", "--model", model_name], check=True)
            model = whisper.load_model(model_name)
        else:
            logger.error(f"模型載入失敗: {e}")
            raise e

    # 轉錄音訊
    logger.info(f"開始音訊轉錄: {input_path}")
    result = model.transcribe(str(input_path))

    # 產生輸出檔案名稱
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = input_path.stem
    txt_filename = f"{timestamp}_{base_name}_transcript.txt"
    
    # 保存結果到新的檔案結構
    output_path = file_manager.get_output_transcript_path(txt_filename, cleaned=False)
    
    # 使用 whisper 的 writer 保存
    output_dir = output_path.parent
    txt_writer = get_writer("txt", str(output_dir))
    txt_writer(result, str(input_path))
    
    # 重新命名檔案以符合我們的命名規範
    original_name = output_dir / f"{input_path.stem}.txt"
    if original_name.exists():
        original_name.rename(output_path)
    
    logger.info(f"轉錄完成: {output_path}")
    return str(output_path)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python transcriber.py <audio_file> [output_dir] [model_name]")
        print("Available models: tiny, base, small, medium, large")
        sys.exit(1)
        
    audio_file = sys.argv[1]
    output_dir = None
    model_name = None
    
    # Parse arguments: second argument could be output path or model name
    for arg in sys.argv[2:]:
        # If it's a directory, set as output path
        if os.path.isdir(arg):
            output_dir = arg
        # Otherwise, if not an audio file, treat as model name
        elif not arg.endswith(('.mp3', '.wav', '.flac', '.m4a')):
            model_name = arg
    
    transcribe_audio(audio_file, output_dir, model_name)