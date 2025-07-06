import torch
import whisper
from whisper.utils import get_writer
import sys
import configparser
import os
import subprocess
import logging

def transcribe_audio(input_path: str, output_dir: str = None, model_name: str = None):
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("transcriber")
    
    # Read configuration file
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    # Use configuration defaults
    if output_dir is None:
        output_dir = config.get('transcriber', 'output_dir', fallback='output/text')
    if model_name is None:
        model_name = config.get('transcriber', 'model_name', fallback='base')
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Check ROCm availability
    if not torch.cuda.is_available():
        logger.info("ROCm not available, using CPU")
    else:
        logger.info(f"Using GPU: {torch.cuda.get_device_name(0)}")

    # Handle path compatibility: replace backslashes with forward slashes
    normalized_path = input_path.replace('\\', '/')
    if not os.path.exists(normalized_path):
        logger.error(f"输入文件不存在: {normalized_path}")
        return None
    
    try:
        # Attempt to load model
        model = whisper.load_model(model_name)
    except RuntimeError as e:
        if "Model" in str(e) and "not found" in str(e):
            logger.info(f"Model {model_name} not found, downloading...")
            # Automatically download model
            subprocess.run(["whisper", "--model", model_name], check=True)
            model = whisper.load_model(model_name)
        else:
            logger.error(f"Model loading failed: {e}")
            raise e

    # Transcribe audio
    logger.info(f"Starting audio transcription: {normalized_path}")
    result = model.transcribe(normalized_path)

    # Save results
    txt_writer = get_writer("txt", output_dir)
    txt_writer(result, normalized_path)

    # Return text file path
    base = os.path.basename(normalized_path)
    base_without_ext = os.path.splitext(base)[0]
    txt_path = os.path.join(output_dir, base_without_ext + ".txt")
    
    logger.info(f"Transcription completed: {txt_path}")
    return txt_path

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