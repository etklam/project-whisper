import argparse
from src.downloader import download_audio
from src.transcriber import transcribe_audio
from src.rewriter import rewrite_text
import os

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Audio Processing and AI Rewriting System')
    parser.add_argument('url', nargs='?', help='Video URL to process')
    parser.add_argument('--batch', help='Batch process URL list file', default='input/urls.txt')
    args = parser.parse_args()
    
    # Single URL processing mode
    if args.url:
        process_url(args.url)
        return
    
    # Batch processing mode
    if os.path.exists(args.batch):
        with open(args.batch, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        
        for url in urls:
            print(f"\nProcessing URL: {url}")
            process_url(url)
    else:
        print(f"Error: Batch file not found: {args.batch}")

def process_url(url):
    """Complete workflow for processing a single URL"""
    try:
        # Ensure output directories exist
        os.makedirs('output/audio', exist_ok=True)
        os.makedirs('output/text', exist_ok=True)
        os.makedirs('output/rewritten', exist_ok=True)
        
        print("Step 1: Downloading audio...")
        audio_path = download_audio(url)
        if not audio_path:
            return
            
        print(f"Audio downloaded: {audio_path}")
        
        print("Step 2: Converting audio to text...")
        text_path = transcribe_audio(audio_path)
        if not text_path:
            return
            
        print(f"Text conversion completed: {text_path}")
        
        print("Step 3: Using AI to rewrite text...")
        # Pass the text file path to rewrite_text
        rewritten_path = rewrite_text(text_path)
        if not rewritten_path:
            return
            
        print(f"Text rewriting completed: {rewritten_path}")
        
        print("✅ Processing completed!")
    except Exception as e:
        print(f"Error during processing: {e}")

if __name__ == "__main__":
    main()