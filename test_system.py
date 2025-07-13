#!/usr/bin/env python3
"""
測試新檔案管理系統的腳本
"""
import sys
import os
import logging
from pathlib import Path

# 添加 src 到路徑
sys.path.append(str(Path(__file__).parent / 'src'))

try:
    from src.file_manager import FileManager
    from src.downloader import download_audio
    from src.transcriber import transcribe_audio
    from src.rewriter import rewrite_text
    from src.cleaner import clean_temp_files
except ImportError as e:
    print(f"❌ 導入模組失敗: {e}")
    print("請確保所有必要的模組都已正確安裝")
    sys.exit(1)

def setup_logging():
    """設定測試日誌"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger("test_system")

def test_file_manager():
    """測試檔案管理器"""
    logger = logging.getLogger("test_file_manager")
    logger.info("🧪 測試檔案管理器...")
    
    try:
        # 初始化檔案管理器
        fm = FileManager()
        logger.info("✅ FileManager 初始化成功")
        
        # 測試路徑取得
        urls_path = fm.get_path('data_input_urls')
        logger.info(f"✅ URLs 路徑: {urls_path}")
        
        # 測試檔案儲存
        test_content = "這是測試內容"
        test_file = fm.save_file(test_content, 'data_input_urls', 'test.txt')
        logger.info(f"✅ 測試檔案已儲存: {test_file}")
        
        # 測試檔案載入
        loaded_content = fm.load_file('data_input_urls', 'test.txt')
        if loaded_content == test_content:
            logger.info("✅ 檔案載入測試成功")
        else:
            logger.error("❌ 檔案載入測試失敗")
            return False
        
        # 清理測試檔案
        fm.delete_file('data_input_urls', 'test.txt')
        logger.info("✅ 測試檔案已清理")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 檔案管理器測試失敗: {e}")
        return False

def test_content_categorization():
    """測試內容分類功能"""
    logger = logging.getLogger("test_categorization")
    logger.info("🧪 測試內容分類功能...")
    
    try:
        fm = FileManager()
        
        # 測試不同類型的內容
        test_cases = [
            ("投資理財股票基金", "finance"),
            ("人工智慧機器學習科技", "technology"),
            ("教育學習課程知識", "education"),
            ("一般內容測試", "general")
        ]
        
        for content, expected_category in test_cases:
            result = fm.categorize_content_by_keywords(content)
            if result == expected_category:
                logger.info(f"✅ 內容分類正確: '{content}' -> {result}")
            else:
                logger.warning(f"⚠️ 內容分類可能不準確: '{content}' -> {result} (期望: {expected_category})")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 內容分類測試失敗: {e}")
        return False

def test_directory_structure():
    """測試目錄結構"""
    logger = logging.getLogger("test_directories")
    logger.info("🧪 測試目錄結構...")
    
    required_dirs = [
        "data/input/urls",
        "data/input/audio/raw",
        "data/input/audio/processed",
        "data/output/transcripts/raw",
        "data/output/transcripts/cleaned",
        "data/output/articles/finance",
        "data/output/articles/technology",
        "data/output/articles/education",
        "data/output/articles/general",
        "data/output/reports",
        "data/temp/downloads",
        "data/temp/processing",
        "data/temp/cache",
        "config/prompts",
        "config/models",
        "logs"
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        logger.error(f"❌ 缺少目錄: {missing_dirs}")
        return False
    else:
        logger.info(f"✅ 所有必要目錄都存在 ({len(required_dirs)} 個)")
        return True

def test_config_files():
    """測試配置檔案"""
    logger = logging.getLogger("test_config")
    logger.info("🧪 測試配置檔案...")
    
    # 檢查主配置檔案
    if not Path("config.ini").exists():
        logger.error("❌ config.ini 不存在")
        return False
    
    # 檢查提示模板檔案
    prompt_files = ["finance.txt", "technology.txt", "education.txt", "general.txt"]
    missing_prompts = []
    
    for prompt_file in prompt_files:
        if not Path(f"config/prompts/{prompt_file}").exists():
            missing_prompts.append(prompt_file)
    
    if missing_prompts:
        logger.error(f"❌ 缺少提示模板: {missing_prompts}")
        return False
    
    logger.info("✅ 所有配置檔案都存在")
    return True

def test_urls_file():
    """測試 URLs 檔案"""
    logger = logging.getLogger("test_urls")
    logger.info("🧪 測試 URLs 檔案...")
    
    try:
        fm = FileManager()
        urls_file = fm.get_path('data_input_urls', 'urls.txt')
        
        if not urls_file.exists():
            # 建立空的 URLs 檔案
            urls_file.touch()
            logger.info("✅ 建立了空的 URLs 檔案")
        else:
            logger.info("✅ URLs 檔案已存在")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ URLs 檔案測試失敗: {e}")
        return False

def run_all_tests():
    """執行所有測試"""
    logger = setup_logging()
    logger.info("🚀 開始系統測試...")
    
    tests = [
        ("目錄結構", test_directory_structure),
        ("配置檔案", test_config_files),
        ("URLs 檔案", test_urls_file),
        ("檔案管理器", test_file_manager),
        ("內容分類", test_content_categorization)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"測試: {test_name}")
        logger.info('='*50)
        
        try:
            if test_func():
                logger.info(f"✅ {test_name} 測試通過")
                passed += 1
            else:
                logger.error(f"❌ {test_name} 測試失敗")
                failed += 1
        except Exception as e:
            logger.error(f"❌ {test_name} 測試出現異常: {e}")
            failed += 1
    
    # 測試結果摘要
    logger.info(f"\n{'='*50}")
    logger.info("📊 測試結果摘要")
    logger.info('='*50)
    logger.info(f"通過: {passed}")
    logger.info(f"失敗: {failed}")
    logger.info(f"總計: {passed + failed}")
    
    if failed == 0:
        logger.info("🎉 所有測試都通過了！系統準備就緒。")
        return True
    else:
        logger.error(f"⚠️ 有 {failed} 個測試失敗，請檢查並修復問題。")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)