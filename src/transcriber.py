import torch
import whisper
from whisper.utils import get_writer
import sys
import configparser
import os
import subprocess

def transcribe_audio(input_path: str, output_dir: str = None, model_name: str = None):
    # 讀取設定檔
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    # 使用設定檔預設值
    if output_dir is None:
        output_dir = config.get('transcriber', 'output_dir', fallback='output/text')
    if model_name is None:
        model_name = config.get('transcriber', 'model_name', fallback='base')
    
    # 建立輸出路徑
    os.makedirs(output_dir, exist_ok=True)
    
    # 檢查 ROCm 可用性
    if not torch.cuda.is_available():
        print("ROCm not available. Using CPU instead.")
    else:
        print(f"Using GPU: {torch.cuda.get_device_name(0)}")

    try:
        # 嘗試載入模型
        model = whisper.load_model(model_name)
    except RuntimeError as e:
        if "Model" in str(e) and "not found" in str(e):
            print(f"Model {model_name} not found. Downloading...")
            # 自動下載模型
            subprocess.run(["whisper", "--model", model_name], check=True)
            model = whisper.load_model(model_name)
            # 重新转录音频
            result = model.transcribe(normalized_path)
            # 保存结果并返回路径
            txt_writer = get_writer("txt", output_dir)
            txt_writer(result, normalized_path)
            base = os.path.basename(normalized_path)
            base_without_ext = os.path.splitext(base)[0]
            txt_path = os.path.join(output_dir, base_without_ext + ".txt")
            return txt_path
        else:
            raise e

    # 處理路徑兼容性：將反斜線替換為正斜線
    normalized_path = input_path.replace('\\', '/')
    if not os.path.exists(normalized_path):
        print(f"Error: Input file '{normalized_path}' does not exist.")
        return
        
    # 確保輸出目錄存在
    os.makedirs(output_dir, exist_ok=True)

    # 轉錄音訊
    result = model.transcribe(normalized_path)

    # 儲存結果
    txt_writer = get_writer("txt", output_dir)
    txt_writer(result, normalized_path)

    srt_writer = get_writer("srt", output_dir)
    srt_writer(result, normalized_path)

    # 返回文本文件路径
    base = os.path.basename(normalized_path)
    base_without_ext = os.path.splitext(base)[0]
    txt_path = os.path.join(output_dir, base_without_ext + ".txt")
    
    print(f"Transcription completed. Text file: {txt_path}")
    return txt_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python transcriber.py <audio_file> [output_dir] [model_name]")
        print("Available models: tiny, base, small, medium, large")
        sys.exit(1)
        
    audio_file = sys.argv[1]
    output_dir = None
    model_name = None
    
    # 解析參數：第二個參數可能是輸出路徑或模型名稱
    for arg in sys.argv[2:]:
        # 如果參數是目錄，設為輸出路徑
        if os.path.isdir(arg):
            output_dir = arg
        # 否則，如果參數不是音訊檔案，則視為模型名稱
        elif not arg.endswith(('.mp3', '.wav', '.flac', '.m4a')):
            model_name = arg
    
    transcribe_audio(audio_file, output_dir, model_name)