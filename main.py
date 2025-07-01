import argparse
from src.downloader import download_audio
from src.transcriber import transcribe_audio
from src.rewriter import rewrite_text
import os

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='音頻處理與AI重寫系統')
    parser.add_argument('url', nargs='?', help='要處理的視頻URL')
    parser.add_argument('--batch', help='批量處理URL列表文件', default='input/urls.txt')
    args = parser.parse_args()
    
    # 單一URL處理模式
    if args.url:
        process_url(args.url)
        return
    
    # 批量處理模式
    if os.path.exists(args.batch):
        with open(args.batch, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        
        for url in urls:
            print(f"\n處理URL: {url}")
            process_url(url)
    else:
        print(f"錯誤: 找不到批量文件 {args.batch}")

import os

def process_url(url):
    """處理單個URL的完整流程"""
    try:
        # 確保輸出目錄存在
        os.makedirs('output/audio', exist_ok=True)
        os.makedirs('output/text', exist_ok=True)
        os.makedirs('output/rewritten', exist_ok=True)
        
        print("步驟1: 下載音頻...")
        audio_path = download_audio(url)
        if not audio_path:
            return
            
        print(f"音頻下載完成: {audio_path}")
        
        print("步驟2: 轉換音頻為文字...")
        text_path = transcribe_audio(audio_path)
        if not text_path:
            return
            
        print(f"文字轉換完成: {text_path}")
        
        print("步驟3: 使用AI重寫文本...")
        # 直接傳遞文本文件路徑給rewrite_text
        rewritten_path = rewrite_text(text_path)
        if not rewritten_path:
            return
            
        print(f"文本重寫完成: {rewritten_path}")
        
        print("✅ 處理完成!")
    except Exception as e:
        print(f"處理過程中發生錯誤: {e}")

if __name__ == "__main__":
    main()