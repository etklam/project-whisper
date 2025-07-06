import argparse
import os
import logging
from src.downloader import download_from_urls
from src.transcriber import transcribe_audio
from src.rewriter import rewrite_text
from src.cleaner import clean_directory

def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("processing.log"),
            logging.StreamHandler()
        ]
    )
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Batch audio processing and AI text rewriting system')
    parser.add_argument('--batch', help='URL list file', default='input/urls.txt')
    parser.add_argument('--input-dir', help='Input directory', default='input/')
    parser.add_argument('--output-dir', help='Output directory', default='output/')
    args = parser.parse_args()

    try:
        # Ensure directories exist
        os.makedirs(args.input_dir, exist_ok=True)
        os.makedirs(args.output_dir, exist_ok=True)
        
        logging.info("Step 1: Downloading all MP3 files...")
        download_from_urls(args.batch, args.input_dir)
        
        logging.info("Step 2: Processing files in directory...")
        process_directory(args.input_dir, args.output_dir)
        
        logging.info("Step 3: Cleaning temporary files...")
        clean_directory(args.input_dir, keep_extensions=['.md'])
        
        logging.info("✅ Processing complete! All files saved as Markdown")
    except Exception as e:
        logging.error(f"Processing failed: {str(e)}")

def process_directory(input_dir, output_dir):
    """Process all audio and text files in directory"""
    # Process all MP3 files
    for file in os.listdir(input_dir):
        if file.endswith('.mp3'):
            mp3_path = os.path.join(input_dir, file)
            logging.info(f"Transcribing audio: {file}")
            txt_path = transcribe_audio(mp3_path, output_dir)
            
            # Immediately rewrite the newly generated text file
            if txt_path:
                logging.info(f"Rewriting text: {os.path.basename(txt_path)}")
                rewrite_text(txt_path, output_dir)
    
    # Process remaining TXT files (may be from previous processing)
    for file in os.listdir(input_dir):
        if file.endswith('.txt'):
            txt_path = os.path.join(input_dir, file)
            logging.info(f"Rewriting text: {file}")
            rewrite_text(txt_path, output_dir)

if __name__ == "__main__":
    main()