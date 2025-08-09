"""
專用清理工具

需求：
1) 可單獨運行，用來清理所有不是本系統的檔案（舊結構與不符合規範的檔案）
2) 完成所有 rewrite 後，清理 Input 與 Output（針對新/舊結構）

保留 API：clean_temp_files、archive_old_files（供測試與相容）
"""

from __future__ import annotations

import argparse
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

try:
    from .file_manager import FileManager
except ImportError:  # 允許以 `python src/cleaner.py` 方式單獨運行
    import sys as _sys
    from pathlib import Path as _Path
    _sys.path.append(str(_Path(__file__).resolve().parent.parent))
    from src.file_manager import FileManager


# ------------------------------
# Logging
# ------------------------------
logger = logging.getLogger("cleaner")


@dataclass(frozen=True)
class DirPolicy:
    path_key: str
    allowed_extensions: Set[str]
    description: str


def _ensure_logger_configured() -> None:
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )


def _delete_file(path: Path, dry_run: bool) -> bool:
    if dry_run:
        logger.info(f"[dry-run] 將刪除: {path}")
        return True
    try:
        path.unlink()
        logger.info(f"已刪除: {path}")
        return True
    except Exception as e:
        logger.error(f"刪除失敗 {path}: {e}")
        return False


def _move_audio_to_new_structure(file_manager: FileManager, src: Path, dry_run: bool) -> Optional[Path]:
    if dry_run:
        target = file_manager.get_path("data_input_audio_raw", src.name)
        logger.info(f"[dry-run] 將移動音訊: {src} -> {target}")
        return target
    try:
        return file_manager.move_file(src, "data_input_audio_raw", src.name)
    except Exception as e:
        logger.error(f"移動音訊失敗 {src}: {e}")
        return None


def _iter_files(paths: Iterable[Path]) -> Iterable[Path]:
    for base in paths:
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if p.is_file():
                yield p


def _sweep_dir_by_policy(base_dir: Path, allowed_exts: Set[str], dry_run: bool) -> Tuple[int, int]:
    deleted = 0
    kept = 0
    for file_path in _iter_files([base_dir]):
        if allowed_exts and file_path.suffix.lower() not in allowed_exts:
            if _delete_file(file_path, dry_run):
                deleted += 1
        else:
            kept += 1
    return deleted, kept


def sweep_non_system_files(file_manager: Optional[FileManager] = None, dry_run: bool = False) -> Dict[str, Dict[str, int]]:
    """清理非系統檔案（安全、可乾跑）

    - 針對新結構的各目錄，刪除不符合副檔名規範的檔案
    - 針對舊結構 `input/`、`output/`：
      - 音訊檔案移動至 `data/input/audio/raw`
      - 其他非 .txt/.md 檔案刪除
    """
    _ensure_logger_configured()

    if file_manager is None:
        file_manager = FileManager()

    # 新結構清理策略
    policies: List[DirPolicy] = [
        DirPolicy("data_input_urls", {".txt"}, "URL 清單與紀錄"),
        DirPolicy("data_input_audio_raw", {".mp3", ".wav", ".m4a", ".flac"}, "原始音訊"),
        DirPolicy("data_input_audio_processed", {".mp3", ".wav", ".m4a", ".flac"}, "處理後音訊"),
        DirPolicy("data_input_config", {".ini", ".json", ".yaml", ".yml", ".txt"}, "輸入設定"),
        DirPolicy("data_output_transcripts_raw", {".txt"}, "原始轉錄"),
        DirPolicy("data_output_transcripts_cleaned", {".txt"}, "清理後轉錄"),
        DirPolicy("data_output_articles_finance", {".md"}, "文章-金融"),
        DirPolicy("data_output_articles_technology", {".md"}, "文章-科技"),
        DirPolicy("data_output_articles_education", {".md"}, "文章-教育"),
        DirPolicy("data_output_articles_general", {".md"}, "文章-一般"),
        DirPolicy("data_output_reports", {".json", ".md", ".txt"}, "報告輸出"),
        DirPolicy("logs", {".log", ".txt"}, "日誌"),
        DirPolicy("config_prompts", {".txt"}, "提示模板"),
        # config_models 內視為外部資源，暫不清理
    ]

    summary: Dict[str, Dict[str, int]] = {}

    # 新結構掃描
    for policy in policies:
        base = file_manager.get_path(policy.path_key)
        deleted, kept = _sweep_dir_by_policy(base, policy.allowed_extensions, dry_run)
        summary[str(base)] = {"deleted": deleted, "kept": kept}

    # 舊結構處理：input/ 與 output/
    legacy_input = file_manager.get_path("input")
    if legacy_input.exists():
        deleted = 0
        moved = 0
        kept = 0
        for p in _iter_files([legacy_input]):
            suffix = p.suffix.lower()
            if suffix in {".mp3", ".wav", ".m4a", ".flac"}:
                if _move_audio_to_new_structure(file_manager, p, dry_run):
                    moved += 1
            elif suffix in {".txt", ".md"}:
                kept += 1
            else:
                if _delete_file(p, dry_run):
                    deleted += 1
        summary[str(legacy_input)] = {"deleted": deleted, "moved": moved, "kept": kept}

    legacy_output = file_manager.get_path("output")
    if legacy_output.exists():
        deleted, kept = _sweep_dir_by_policy(legacy_output, {".md", ".txt", ".json"}, dry_run)
        summary[str(legacy_output)] = {"deleted": deleted, "kept": kept}

    logger.info(f"非系統檔案清理摘要: {summary}")
    return summary


def post_rewrite_cleanup(
    file_manager: Optional[FileManager] = None,
    dry_run: bool = False,
    include_legacy_io: bool = True,
) -> Dict[str, Dict[str, int]]:
    """完成所有 rewrite 後清場

    - 刪除：data/input/audio/{raw,processed} 全部音訊
    - 刪除：data/output/transcripts/{raw,cleaned} 全部逐字稿
    - 清空：data/temp/*
    - 保留：articles/*、reports/*、config/*、logs/*
    - 可選：清空舊結構 input/ 與 output/
    """
    _ensure_logger_configured()

    if file_manager is None:
        file_manager = FileManager()

    targets: List[Tuple[str, Set[str]]] = [
        ("data_input_audio_raw", set()),
        ("data_input_audio_processed", set()),
        ("data_output_transcripts_raw", set()),
        ("data_output_transcripts_cleaned", set()),
    ]

    summary: Dict[str, Dict[str, int]] = {}

    for key, _ in targets:
        base = file_manager.get_path(key)
        deleted = 0
        kept = 0
        for p in _iter_files([base]):
            if _delete_file(p, dry_run):
                deleted += 1
        summary[str(base)] = {"deleted": deleted, "kept": kept}

    # 清空 temp/*
    cleaned_temp = clean_temp_files(file_manager=file_manager, older_than_hours=0 if not dry_run else 0)
    summary["data/temp/*"] = {"deleted": cleaned_temp}

    # 可選：清空舊結構
    if include_legacy_io:
        for legacy_key in ("input", "output"):
            base = file_manager.get_path(legacy_key)
            if not base.exists():
                continue
            deleted = 0
            for p in _iter_files([base]):
                if _delete_file(p, dry_run):
                    deleted += 1
            summary[str(base)] = {"deleted": deleted}

    logger.info(f"完成 rewrite 後清理摘要: {summary}")
    return summary


def clean_temp_files(file_manager: Optional[FileManager] = None, older_than_hours: int = 24) -> int:
    """清理暫存檔案（相容 API）"""
    _ensure_logger_configured()

    if file_manager is None:
        file_manager = FileManager()
    try:
        cleaned_count = file_manager.clean_temp_files(older_than_hours)
        logger.info(f"暫存檔案清理完成: 清理了 {cleaned_count} 個檔案")
        return cleaned_count
    except Exception as e:
        logger.error(f"清理暫存檔案失敗: {e}")
        return 0


def archive_old_files(file_manager: Optional[FileManager] = None, days_old: int = 30) -> int:
    """歸檔舊轉錄檔案（相容 API）"""
    _ensure_logger_configured()

    if file_manager is None:
        file_manager = FileManager()

    from datetime import datetime, timedelta

    cutoff_date = datetime.now() - timedelta(days=days_old)
    cutoff_timestamp = cutoff_date.timestamp()

    archived_count = 0
    try:
        transcripts_dir = file_manager.get_path("data_output_transcripts_raw")
        for file_path in transcripts_dir.glob("*.txt"):
            if file_path.stat().st_mtime < cutoff_timestamp:
                archive_path = file_manager.get_path("data_output_reports") / "archived" / "transcripts"
                archive_path.mkdir(parents=True, exist_ok=True)
                new_path = archive_path / file_path.name
                file_path.rename(new_path)
                archived_count += 1
                logger.info(f"已歸檔轉錄檔案: {file_path} -> {new_path}")
        logger.info(f"檔案歸檔完成: 歸檔了 {archived_count} 個檔案")
        return archived_count
    except Exception as e:
        logger.error(f"歸檔檔案失敗: {e}")
        return 0


def clean_directory(
    directory: Optional[str] = None,
    keep_extensions: Optional[List[str]] = None,
    file_manager: Optional[FileManager] = None,
) -> bool:
    """相容舊版 API：清理指定目錄

    規則：
    - 保留 keep_extensions 副檔名（預設 .md/.txt）
    - 音訊檔 (.mp3/.wav/.m4a/.flac) 會搬移到 data/input/audio/raw
    - 其餘檔案刪除
    """
    _ensure_logger_configured()

    if file_manager is None:
        file_manager = FileManager()

    if directory is None:
        directory = "input"

    base = Path(directory)
    if not base.exists():
        logger.error(f"目錄不存在: {directory}")
        return False

    if keep_extensions is None:
        keep_extensions = [".md", ".txt"]
    keep_set = {ext.lower() for ext in keep_extensions}

    files_deleted = 0
    files_moved = 0
    files_kept = 0

    for p in _iter_files([base]):
        suffix = p.suffix.lower()
        if suffix in keep_set:
            files_kept += 1
            continue
        if suffix in {".mp3", ".wav", ".m4a", ".flac"}:
            if _move_audio_to_new_structure(file_manager, p, dry_run=False):
                files_moved += 1
            continue
        if _delete_file(p, dry_run=False):
            files_deleted += 1

    logger.info(
        f"清理完成: 保留 {files_kept}、移動音訊 {files_moved}、刪除 {files_deleted} (目錄: {base})"
    )
    return True


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Project Whisper 清理工具")
    parser.add_argument(
        "--mode",
        choices=["sweep-non-system", "post-rewrite", "clean-temp", "archive-old"],
        required=True,
        help="選擇清理模式",
    )
    parser.add_argument("--dry-run", action="store_true", help="顯示將執行的操作但不實際刪除")
    parser.add_argument("--older-than-hours", type=int, default=24, help="clean-temp 模式使用的時間閾值")
    parser.add_argument("--days-old", type=int, default=30, help="archive-old 模式使用的天數閾值")
    parser.add_argument(
        "--no-legacy",
        action="store_true",
        help="post-rewrite 模式下不清理舊結構 input/ 與 output/",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    _ensure_logger_configured()
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    fm = FileManager()

    if args.mode == "sweep-non-system":
        sweep_non_system_files(fm, dry_run=args.dry_run)
        return 0
    if args.mode == "post-rewrite":
        post_rewrite_cleanup(fm, dry_run=args.dry_run, include_legacy_io=not args.no_legacy)
        return 0
    if args.mode == "clean-temp":
        clean_temp_files(fm, older_than_hours=args.older_than_hours)
        return 0
    if args.mode == "archive-old":
        archive_old_files(fm, days_old=args.days_old)
        return 0

    parser.error("未知的模式")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())