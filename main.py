import argparse
import os
import logging
from datetime import datetime
from pathlib import Path
from src.file_manager import FileManager
from src.downloader import download_from_urls
from src.transcriber import transcribe_audio
from src.rewriter import rewrite_text
from src.cleaner import clean_directory, clean_temp_files

def main():
    """主要處理函數"""
    # 初始化檔案管理器
    file_manager = FileManager()
    
    # 配置日誌
    log_file = file_manager.get_path('logs') / f"processing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger("main")
    
    # 解析命令列參數
    parser = argparse.ArgumentParser(description='批次音訊處理和 AI 文字重寫系統')
    parser.add_argument('--batch', help='URL 清單檔案',
                       default=str(file_manager.get_path('data_input_urls', 'urls.txt')))
    parser.add_argument('--clean-only', action='store_true', help='僅執行清理作業')
    parser.add_argument('--no-download', action='store_true', help='跳過下載步驟')
    parser.add_argument('--category', help='指定文章分類 (finance, technology, education, general)')
    parser.add_argument('--prompt-type', help='指定提示類型 (finance, technology, education)')
    args = parser.parse_args()

    try:
        logger.info("🚀 開始處理流程...")
        
        # 如果只是清理模式
        if args.clean_only:
            logger.info("執行清理模式...")
            clean_old_structure(file_manager)
            clean_temp_files(file_manager)
            logger.info("✅ 清理完成!")
            return
        
        # 步驟 1: 下載 MP3 檔案
        if not args.no_download:
            logger.info("步驟 1: 下載所有 MP3 檔案...")
            success = download_from_urls(args.batch, file_manager)
            if not success:
                logger.warning("下載過程中出現問題，但繼續處理現有檔案...")
        else:
            logger.info("跳過下載步驟...")
        
        # 步驟 2: 處理音訊檔案
        logger.info("步驟 2: 處理音訊檔案...")
        process_audio_files(file_manager, args.category, args.prompt_type)
        
        # 步驟 3: 清理暫存檔案，這是新的第三步驟
        logger.info("步驟 4: 清理暫存檔案...")
        clean_temp_files(file_manager)
        
        # 產生處理報告
        generate_summary_report(file_manager)
        
        logger.info("✅ 處理完成! 所有檔案已儲存為 Markdown")
        
    except Exception as e:
        logger.error(f"處理失敗: {str(e)}")
        raise

def process_audio_files(file_manager, category=None, prompt_type=None):
    """處理所有音訊檔案"""
    logger = logging.getLogger("process_audio")
    
    # 取得所有音訊檔案
    audio_files = file_manager.list_files('data_input_audio_raw', '*.mp3')
    
    if not audio_files:
        logger.info("沒有找到音訊檔案")
        return
    
    for audio_file in audio_files:
        try:
            logger.info(f"轉錄音訊: {audio_file.name}")
            
            # 轉錄音訊
            txt_path = transcribe_audio(str(audio_file), file_manager)
            
            if txt_path:
                logger.info(f"重寫文字: {Path(txt_path).name}")
                
                # 立即重寫新產生的文字檔案
                rewrite_text(txt_path, file_manager, prompt_type, category)
                
        except Exception as e:
            logger.error(f"處理音訊檔案失敗 {audio_file}: {e}")
# 刪除多餘的文字處理步驟 3
# def process_text_files(file_manager, category=None, prompt_type=None):
#     """處理現有的文字檔案"""
#     logger = logging.getLogger("process_text")
#
#     # 處理原始轉錄檔案
#     text_files = file_manager.list_files('data_output_transcripts_raw', '*.txt')
#
#     for text_file in text_files:
#         try:
#             logger.info(f"重寫文字: {text_file.name}")
#             rewrite_text(str(text_file), file_manager, prompt_type, category)
#
#         except Exception as e:
#             logger.error(f"處理文字檔案失敗 {text_file}: {e}")
    """處理現有的文字檔案"""
    logger = logging.getLogger("process_text")
    
    # 處理原始轉錄檔案
    text_files = file_manager.list_files('data_output_transcripts_raw', '*.txt')
    
    for text_file in text_files:
        try:
            logger.info(f"重寫文字: {text_file.name}")
            rewrite_text(str(text_file), file_manager, prompt_type, category)
            
        except Exception as e:
            logger.error(f"處理文字檔案失敗 {text_file}: {e}")

def clean_old_structure(file_manager):
    """清理舊的檔案結構"""
    logger = logging.getLogger("clean_old")
    
    # 清理舊的 input 目錄
    if Path("input").exists():
        logger.info("清理舊的 input 目錄...")
        clean_directory("input", ['.md'], file_manager)
    
    # 清理舊的 output 目錄
    if Path("output").exists():
        logger.info("清理舊的 output 目錄...")
        clean_directory("output", ['.md'], file_manager)

def generate_summary_report(file_manager):
    """產生處理摘要報告"""
    logger = logging.getLogger("report")
    
    try:
        # 統計各類檔案數量
        stats = {
            'audio_files': len(file_manager.list_files('data_input_audio_raw', '*.mp3')),
            'transcript_files': len(file_manager.list_files('data_output_transcripts_raw', '*.txt')),
            'article_files': {
                'finance': len(file_manager.list_files('data_output_articles_finance', '*.md')),
                'technology': len(file_manager.list_files('data_output_articles_technology', '*.md')),
                'education': len(file_manager.list_files('data_output_articles_education', '*.md')),
                'general': len(file_manager.list_files('data_output_articles_general', '*.md'))
            },
            'total_articles': 0
        }
        
        stats['total_articles'] = sum(stats['article_files'].values())
        
        # 建立摘要報告
        batch_id = f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        file_manager.create_processing_report(batch_id, stats)
        
        logger.info(f"📊 處理摘要:")
        logger.info(f"   音訊檔案: {stats['audio_files']}")
        logger.info(f"   轉錄檔案: {stats['transcript_files']}")
        logger.info(f"   文章總數: {stats['total_articles']}")
        logger.info(f"     - 理財: {stats['article_files']['finance']}")
        logger.info(f"     - 科技: {stats['article_files']['technology']}")
        logger.info(f"     - 教育: {stats['article_files']['education']}")
        logger.info(f"     - 一般: {stats['article_files']['general']}")
        
    except Exception as e:
        logger.error(f"產生摘要報告失敗: {e}")

if __name__ == "__main__":
    main()