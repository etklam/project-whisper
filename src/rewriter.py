import requests
import configparser
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from .prompt import PROMPTS
from .file_manager import FileManager


def _get_config_value(config: configparser.ConfigParser, sections, key: str, fallback=None):
    """Helper to read config with flexible section casing and lowercased keys."""
    for section in sections:
        if config.has_option(section, key):
            return config.get(section, key)
    return fallback


def _load_prompt_text(prompt_type: str, prompts_dir: Path) -> str:
    """Load prompt text from in-code PROMPTS or config/prompts fallback."""
    if prompt_type in PROMPTS:
        return PROMPTS[prompt_type].strip()

    # Fallback to external prompt files under config/prompts/{type}.txt
    candidate_file = prompts_dir / f"{prompt_type}.txt"
    if candidate_file.exists():
        return candidate_file.read_text(encoding="utf-8").strip()

    # Final fallback to general if available, otherwise finance
    if "general" in PROMPTS:
        return PROMPTS["general"].strip()
    if (prompts_dir / "general.txt").exists():
        return (prompts_dir / "general.txt").read_text(encoding="utf-8").strip()
    # As last resort use finance if present
    if "finance" in PROMPTS:
        return PROMPTS["finance"].strip()
    if (prompts_dir / "finance.txt").exists():
        return (prompts_dir / "finance.txt").read_text(encoding="utf-8").strip()

    # If nothing found, return a simple generic instruction
    return "你是一位專業內容編輯，請將使用者提供的逐字稿重寫成結構化、清晰的 Markdown 文章。"


def _call_openrouter(api_key: str, endpoint: str, model: str, system_prompt: str, user_content: str, timeout: int = 120) -> str:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    "請根據上述系統身份與工作流程，將以下逐字稿重寫為結構化、條理清晰、適合年輕讀者閱讀的 Markdown 文章。\n\n"
                    "逐字稿：\n\n" + user_content
                ),
            },
        ],
    }

    response = requests.post(endpoint, json=payload, headers=headers, timeout=timeout)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


def _limit_filename_base(base: str, max_len: int = 15) -> str:
    return base[:max_len] if len(base) > max_len else base


def rewrite_text(
    text_file: str,
    file_manager: Optional[FileManager] = None,
    prompt_type: Optional[str] = None,
    category: Optional[str] = None,
) -> Optional[str]:
    """使用 OpenRouter API 重寫文字檔案並儲存為 Markdown

    Args:
        text_file: 文字檔案路徑
        file_manager: 檔案管理器實例
        prompt_type: 提示類型 (finance, technology, education, general)
        category: 文章分類；None 時可自動分類

    Returns:
        已儲存的 Markdown 檔案路徑字串，若失敗則回傳 None
    """

    logger = logging.getLogger("rewriter")

    if file_manager is None:
        file_manager = FileManager()

    text_path = Path(text_file)
    if not text_path.exists():
        logger.error(f"文字檔案不存在: {text_path}")
        return None

    # Read config
    config = configparser.ConfigParser()
    config.read("config.ini")

    api_key = _get_config_value(config, ["openrouter", "OPENROUTER"], "api_key")
    if not api_key:
        logger.error("OpenRouter API 金鑰未設定 (config.ini [OPENROUTER] API_KEY)")
        return None

    endpoint = _get_config_value(
        config, ["rewriter", "REWRITER"], "endpoint", "https://openrouter.ai/api/v1/chat/completions"
    )
    model = _get_config_value(
        config, ["rewriter", "REWRITER"], "model", "deepseek/deepseek-chat-v3-0324:free"
    )
    default_prompt_type = _get_config_value(
        config, ["rewriter", "REWRITER"], "prompt", "finance"
    )
    auto_categorize = _get_config_value(
        config, ["rewriter", "REWRITER"], "auto_categorize_output", "true"
    )
    auto_categorize = str(auto_categorize).strip().lower() in {"1", "true", "yes", "y"}

    effective_prompt_type = (prompt_type or default_prompt_type or "general").strip().lower()

    # Load transcript content
    try:
        transcript_text = text_path.read_text(encoding="utf-8")
    except Exception as e:
        logger.error(f"讀取文字檔案失敗: {e}")
        return None

    # Load system prompt
    prompts_dir = file_manager.get_path("config_prompts")
    system_prompt = _load_prompt_text(effective_prompt_type, prompts_dir)

    # Call OpenRouter to rewrite
    try:
        logger.info(
            f"呼叫 OpenRouter 重寫內容 (model={model}, prompt={effective_prompt_type})"
        )
        rewritten_content = _call_openrouter(api_key, endpoint, model, system_prompt, transcript_text)
        # Cooldown to avoid rate limits
        time.sleep(10)
    except Exception as e:
        logger.error(f"OpenRouter 重寫失敗: {e}")
        return None

    # Decide category
    final_category = category
    if not final_category and auto_categorize:
        try:
            final_category = file_manager.categorize_content_by_keywords(rewritten_content)
        except Exception:
            final_category = "general"
    if not final_category:
        final_category = "general"

    # Build filename: {timestamp}_{basename15}_{prompt}.md
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = text_path.stem
    # Strip common suffix like _transcript
    if base_name.endswith("_transcript"):
        base_name = base_name[: -len("_transcript")]
    base_name = _limit_filename_base(base_name)
    safe_prompt = effective_prompt_type.replace("/", "-")
    filename = f"{timestamp}_{base_name}_{safe_prompt}.md"

    # Save to category directory
    try:
        saved_path = file_manager.save_file(
            rewritten_content, f"data_output_articles_{final_category}", filename
        )
        logger.info(f"重寫完成並已儲存: {saved_path}")
        return str(saved_path)
    except Exception as e:
        logger.error(f"儲存重寫結果失敗: {e}")
        return None
