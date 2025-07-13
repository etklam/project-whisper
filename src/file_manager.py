"""
檔案管理器 - 統一管理專案中的檔案操作和路徑
"""
import os
import shutil
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

class FileManager:
    """統一的檔案管理器"""
    
    def __init__(self, base_dir: str = "."):
        """初始化檔案管理器
        
        Args:
            base_dir: 專案根目錄
        """
        self.base_dir = Path(base_dir)
        self.setup_directories()
        self.logger = logging.getLogger(__name__)
        
    def setup_directories(self):
        """設定目錄結構"""
        # 定義目錄結構
        self.dirs = {
            # 舊有的輸入目錄 (保持向後相容)
            'input': self.base_dir / 'input',
            
            # 新的資料目錄結構
            'data_input_urls': self.base_dir / 'data' / 'input' / 'urls',
            'data_input_audio_raw': self.base_dir / 'data' / 'input' / 'audio' / 'raw',
            'data_input_audio_processed': self.base_dir / 'data' / 'input' / 'audio' / 'processed',
            'data_input_config': self.base_dir / 'data' / 'input' / 'config',
            
            'data_output_transcripts_raw': self.base_dir / 'data' / 'output' / 'transcripts' / 'raw',
            'data_output_transcripts_cleaned': self.base_dir / 'data' / 'output' / 'transcripts' / 'cleaned',
            'data_output_articles_finance': self.base_dir / 'data' / 'output' / 'articles' / 'finance',
            'data_output_articles_technology': self.base_dir / 'data' / 'output' / 'articles' / 'technology',
            'data_output_articles_education': self.base_dir / 'data' / 'output' / 'articles' / 'education',
            'data_output_articles_general': self.base_dir / 'data' / 'output' / 'articles' / 'general',
            'data_output_reports': self.base_dir / 'data' / 'output' / 'reports',
            
            'data_temp_downloads': self.base_dir / 'data' / 'temp' / 'downloads',
            'data_temp_processing': self.base_dir / 'data' / 'temp' / 'processing',
            'data_temp_cache': self.base_dir / 'data' / 'temp' / 'cache',
            
            'config_prompts': self.base_dir / 'config' / 'prompts',
            'config_models': self.base_dir / 'config' / 'models',
            
            'logs': self.base_dir / 'logs',
            
            # 舊有的輸出目錄 (保持向後相容)
            'output': self.base_dir / 'output'
        }
        
        # 建立所有目錄
        for dir_path in self.dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def get_path(self, category: str, filename: str = None) -> Path:
        """取得指定類別的路徑
        
        Args:
            category: 目錄類別
            filename: 檔案名稱 (可選)
            
        Returns:
            完整路徑
        """
        if category not in self.dirs:
            raise ValueError(f"未知的目錄類別: {category}。可用類別: {list(self.dirs.keys())}")
        
        path = self.dirs[category]
        if filename:
            path = path / filename
        
        return path
    
    def get_input_audio_path(self, filename: str, processed: bool = False) -> Path:
        """取得音訊檔案路徑
        
        Args:
            filename: 檔案名稱
            processed: 是否為處理過的檔案
            
        Returns:
            音訊檔案路徑
        """
        category = 'data_input_audio_processed' if processed else 'data_input_audio_raw'
        return self.get_path(category, filename)
    
    def get_output_transcript_path(self, filename: str, cleaned: bool = False) -> Path:
        """取得轉錄檔案路徑
        
        Args:
            filename: 檔案名稱
            cleaned: 是否為清理過的檔案
            
        Returns:
            轉錄檔案路徑
        """
        category = 'data_output_transcripts_cleaned' if cleaned else 'data_output_transcripts_raw'
        return self.get_path(category, filename)
    
    def get_output_article_path(self, filename: str, category: str = 'general') -> Path:
        """取得文章檔案路徑
        
        Args:
            filename: 檔案名稱
            category: 文章類別 (finance, technology, education, general)
            
        Returns:
            文章檔案路徑
        """
        dir_category = f'data_output_articles_{category}'
        return self.get_path(dir_category, filename)
    
    def save_file(self, content: str, category: str, filename: str, 
                  encoding: str = 'utf-8') -> Path:
        """儲存檔案
        
        Args:
            content: 檔案內容
            category: 目錄類別
            filename: 檔案名稱
            encoding: 編碼格式
            
        Returns:
            儲存的檔案路徑
        """
        file_path = self.get_path(category, filename)
        
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        
        self.logger.info(f"檔案已儲存: {file_path}")
        return file_path
    
    def load_file(self, category: str, filename: str, 
                  encoding: str = 'utf-8') -> str:
        """載入檔案
        
        Args:
            category: 目錄類別
            filename: 檔案名稱
            encoding: 編碼格式
            
        Returns:
            檔案內容
        """
        file_path = self.get_path(category, filename)
        
        if not file_path.exists():
            raise FileNotFoundError(f"檔案不存在: {file_path}")
        
        with open(file_path, 'r', encoding=encoding) as f:
            content = f.read()
        
        self.logger.info(f"檔案已載入: {file_path}")
        return content
    
    def move_file(self, source_path: Path, target_category: str, 
                  target_filename: str = None) -> Path:
        """移動檔案
        
        Args:
            source_path: 來源檔案路徑
            target_category: 目標目錄類別
            target_filename: 目標檔案名稱 (可選)
            
        Returns:
            目標檔案路徑
        """
        source_path = Path(source_path)
        target_filename = target_filename or source_path.name
        target_path = self.get_path(target_category, target_filename)
        
        if not source_path.exists():
            raise FileNotFoundError(f"來源檔案不存在: {source_path}")
        
        shutil.move(str(source_path), str(target_path))
        self.logger.info(f"檔案已移動: {source_path} -> {target_path}")
        return target_path
    
    def copy_file(self, source_path: Path, target_category: str,
                  target_filename: str = None) -> Path:
        """複製檔案
        
        Args:
            source_path: 來源檔案路徑
            target_category: 目標目錄類別
            target_filename: 目標檔案名稱 (可選)
            
        Returns:
            目標檔案路徑
        """
        source_path = Path(source_path)
        target_filename = target_filename or source_path.name
        target_path = self.get_path(target_category, target_filename)
        
        if not source_path.exists():
            raise FileNotFoundError(f"來源檔案不存在: {source_path}")
        
        shutil.copy2(str(source_path), str(target_path))
        self.logger.info(f"檔案已複製: {source_path} -> {target_path}")
        return target_path
    
    def delete_file(self, category: str, filename: str) -> bool:
        """刪除檔案
        
        Args:
            category: 目錄類別
            filename: 檔案名稱
            
        Returns:
            是否成功刪除
        """
        file_path = self.get_path(category, filename)
        
        if not file_path.exists():
            self.logger.warning(f"檔案不存在，無法刪除: {file_path}")
            return False
        
        file_path.unlink()
        self.logger.info(f"檔案已刪除: {file_path}")
        return True
    
    def list_files(self, category: str, pattern: str = "*") -> List[Path]:
        """列出目錄中的檔案
        
        Args:
            category: 目錄類別
            pattern: 檔案模式 (如 "*.txt", "*.mp3")
            
        Returns:
            檔案路徑列表
        """
        dir_path = self.get_path(category)
        files = list(dir_path.glob(pattern))
        files = [f for f in files if f.is_file()]
        return sorted(files)
    
    def clean_temp_files(self, older_than_hours: int = 24) -> int:
        """清理暫存檔案
        
        Args:
            older_than_hours: 清理多少小時前的檔案
            
        Returns:
            清理的檔案數量
        """
        import time
        
        temp_dirs = ['data_temp_downloads', 'data_temp_processing', 'data_temp_cache']
        cleaned_count = 0
        cutoff_time = time.time() - (older_than_hours * 3600)
        
        for temp_dir in temp_dirs:
            dir_path = self.get_path(temp_dir)
            for file_path in dir_path.rglob('*'):
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    try:
                        file_path.unlink()
                        cleaned_count += 1
                        self.logger.info(f"已清理暫存檔案: {file_path}")
                    except Exception as e:
                        self.logger.error(f"清理檔案失敗 {file_path}: {e}")
        
        self.logger.info(f"暫存檔案清理完成，共清理 {cleaned_count} 個檔案")
        return cleaned_count
    
    def get_file_info(self, category: str, filename: str) -> Dict:
        """取得檔案資訊
        
        Args:
            category: 目錄類別
            filename: 檔案名稱
            
        Returns:
            檔案資訊字典
        """
        file_path = self.get_path(category, filename)
        
        if not file_path.exists():
            raise FileNotFoundError(f"檔案不存在: {file_path}")
        
        stat = file_path.stat()
        return {
            'path': str(file_path),
            'size': stat.st_size,
            'created': datetime.fromtimestamp(stat.st_ctime),
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'extension': file_path.suffix,
            'name': file_path.stem
        }
    
    def generate_unique_filename(self, category: str, base_name: str, 
                                extension: str = "") -> str:
        """產生唯一的檔案名稱
        
        Args:
            category: 目錄類別
            base_name: 基礎檔案名稱
            extension: 副檔名
            
        Returns:
            唯一的檔案名稱
        """
        if not extension.startswith('.') and extension:
            extension = '.' + extension
        
        counter = 1
        filename = f"{base_name}{extension}"
        
        while self.get_path(category, filename).exists():
            filename = f"{base_name}_{counter}{extension}"
            counter += 1
        
        return filename
    
    def categorize_content_by_keywords(self, content: str, title: str = "") -> str:
        """根據關鍵字分類內容
        
        Args:
            content: 內容文字
            title: 標題文字
            
        Returns:
            分類結果 (finance, technology, education, general)
        """
        text = (content + " " + title).lower()
        
        # 定義關鍵字
        categories = {
            'finance': [
                '投資', '股票', '基金', '理財', '金融', '銀行', '保險', '債券',
                '經濟', '市場', '財務', '資產', '收益', '風險', '投資組合',
                'finance', 'investment', 'stock', 'fund', 'money', 'financial'
            ],
            'technology': [
                '科技', '技術', '軟體', '硬體', '程式', '開發', 'AI', '人工智慧',
                '機器學習', '區塊鏈', '雲端', '數據', '演算法', '網路', '資安',
                'technology', 'software', 'hardware', 'programming', 'development'
            ],
            'education': [
                '教育', '學習', '課程', '教學', '知識', '技能', '培訓', '研究',
                '學術', '大學', '學校', '考試', '證照', '專業', '能力',
                'education', 'learning', 'course', 'teaching', 'knowledge'
            ]
        }
        
        # 計算分數
        scores = {}
        for category, keywords in categories.items():
            score = sum(1 for keyword in keywords if keyword in text)
            scores[category] = score
        
        # 返回最高分的類別
        max_score = max(scores.values())
        if max_score == 0:
            return 'general'
        
        for category, score in scores.items():
            if score == max_score:
                return category
        
        return 'general'
    
    def create_processing_report(self, batch_id: str, stats: Dict) -> Path:
        """建立處理報告
        
        Args:
            batch_id: 批次ID
            stats: 統計資料
            
        Returns:
            報告檔案路徑
        """
        report = {
            'batch_id': batch_id,
            'timestamp': datetime.now().isoformat(),
            'statistics': stats
        }
        
        filename = f"processing_report_{batch_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = self.get_path('data_output_reports', filename)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        
        self.logger.info(f"處理報告已建立: {report_path}")
        return report_path