import torch
import whisper
from whisper.utils import get_writer
import sys
import configparser
import os
import subprocess

def transcribe_audio(input_path: str, output_dir: str = None, model_name: str = None):
    # Read configuration file
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    # Use configuration defaults
    if output_dir is None:
        output_dir = config.get('transcriber', 'output_dir', fallback='output/text')
    if model_name is None:
        model_name = config.get('transcriber', 'model_name', fallback='base')
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Check ROCm availability
    if not torch.cuda.is_available():
        print("ROCm not available. Using CPU instead.")
    else:
        print(f"Using GPU: {torch.cuda.get_device_name(0)}")

    try:
        # Try to load model
        model = whisper.load_model(model_name)
    except RuntimeError as e:
        if "Model" in str(e) and "not found" in str(e):
            print(f"Model {model_name} not found. Downloading...")
            # Automatically download model
            subprocess.run(["whisper", "--model", model_name], check=True)
            model = whisper.load_model(model_name)
            # Retranscribe audio
            result = model.transcribe(normalized_path)
            # Save results and return path
            txt_writer = get_writer("txt", output_dir)
            txt_writer(result, normalized_path)
            base = os.path.basename(normalized_path)
            base_without_ext = os.path.splitext(base)[0]
            txt_path = os.path.join(output_dir, base_without_ext + ".txt")
            return txt_path
        else:
            raise e

    # Handle path compatibility: replace backslashes with forward slashes
    normalized_path = input_path.replace('\\', '/')
    if not os.path.exists(normalized_path):
        print(f"Error: Input file '{normalized_path}' does not exist.")
        return None
        
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Transcribe audio
    result = model.transcribe(normalized_path)

    # Save results
    txt_writer = get_writer("txt", output_dir)
    txt_writer(result, normalized_path)

    # Return text file path
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
    
    # Parse arguments: second argument could be output path or model name
    for arg in sys.argv[2:]:
        # If argument is a directory, set as output path
        if os.path.isdir(arg):
            output_dir = arg
        # Otherwise, if not an audio file, treat as model name
        elif not arg.endswith(('.mp3', '.wav', '.flac', '.m4a')):
            model_name = arg
    
    transcribe_audio(audio_file, output_dir, model_name)