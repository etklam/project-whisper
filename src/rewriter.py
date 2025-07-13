import requests
import configparser
import os
import logging
from datetime import datetime
from pathlib import Path
from .prompt import PROMPTS
from .file_manager import FileManager

def rewrite_text(text_file, file_manager=None, prompt_type=None, category=None):
    """使用 OpenRouter API 重寫文字檔案並儲存為 Markdown
    
    Args:
        text_file (str): 文字檔案路徑
        file_manager (FileManager): 檔案管理器實例
        prompt_type (str): 提示類型 (finance, technology, education)
        category (str): 文章分類，如果為 None 則自動分類
    """
    # 配置日誌
    logger = logging.getLogger("rewriter")
    
    if file_manager is None:
        file_manager = FileManager()
    
    # 取得檔案基本名稱
    text_path = Path(text_file)
    base_name = text_path.stem
    
    # 讀取文字檔案內容
    try:
        with open(text_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # 翻譯為英文 (保持原有功能)
        from .utils import translate_to_english
        text = translate_to_english(text)
        
        logger.info(f"成功讀取文字檔案: {text_file}")
    except Exception as e:
        logger.error(f"讀取文字檔案失敗: {e}")
        return None
    
    # 讀取配置
    config = configparser.ConfigParser()
    config.read('config.ini')
    api_key = config.get('OPENROUTER', 'API_KEY', fallback='your_api_key_here')
    
    if not api_key or api_key == 'your_api_key_here':
        logger.error("錯誤: 請在 config.ini 中配置有效的 OpenRouter API 金鑰")
        return None
    
    # 讀取提示類型
    if prompt_type is None:
        prompt_type = config.get('REWRITER', 'PROMPT', fallback='finance').lower()
    
    # 自動分類 (如果啟用且未指定分類)
    if category is None:
        auto_categorize = config.getboolean('REWRITER', 'auto_categorize_output', fallback=True)
        if auto_categorize:
            category = file_manager.categorize_content_by_keywords(text)
        else:
            category = 'general'
    
    try:
        # 呼叫 OpenRouter API
        logger.info(f"開始文字重寫: {text_file}")
        response = requests.post(
            config.get('REWRITER', 'ENDPOINT', fallback="https://openrouter.ai/api/v1/chat/completions"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": config.get('REWRITER', 'MODEL', fallback="deepseek/deepseek-chat-v3-0324:free"),
                "messages": [
                    {
                        "role": "system",
                        "content": PROMPTS.get(prompt_type, PROMPTS['finance'])
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ]
            }
        )
        
        # 檢查回應狀態
        response.raise_for_status()
        
        # 取得重寫的文字
        rewritten_text = response.json()['choices'][0]['message']['content']
        
        # 產生輸出檔案名稱
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        md_filename = f"{timestamp}_{base_name}_{prompt_type}.md"
        
        # 儲存到對應的分類目錄
        output_path = file_manager.get_output_article_path(md_filename, category)
        
        # 儲存重寫的文字
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(rewritten_text)
        
        # 建立處理報告
        stats = {
            'input_file': str(text_file),
            'output_file': str(output_path),
            'category': category,
            'prompt_type': prompt_type,
            'original_length': len(text),
            'rewritten_length': len(rewritten_text)
        }
        
        batch_id = f"rewrite_{timestamp}"
        file_manager.create_processing_report(batch_id, stats)
        
        logger.info(f"文字重寫完成: {output_path}")
        logger.info(f"分類: {category}")
        return str(output_path)
        
    except Exception as e:
        logger.error(f"文字重寫失敗: {e}")
        return None