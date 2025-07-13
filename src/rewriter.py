import requests
import configparser
import os
import logging
from .prompt import PROMPTS  # 新增PROMPTS導入

def rewrite_text(text_file, output_dir="output/"):
    """Rewrite a text file using the OpenRouter API and save as Markdown
    
    Args:
        text_file (str): Path to the text file to rewrite
        output_dir (str): Output directory (default: 'output/')
    """
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("rewriter")
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract base name from input file
    base_name = os.path.splitext(os.path.basename(text_file))[0]
    
    # Read text file content
    try:
        with open(text_file, 'r', encoding='utf-8') as f:
            text = f.read()
        from .utils import translate_to_english
        text = translate_to_english(text)
        
        logger.info(f"Successfully read text file: {text_file}")
    except Exception as e:
        logger.error(f"Failed to read text file: {e}")
        return None
    
    # Read API key from config
    config = configparser.ConfigParser()
    config.read('config.ini')
    api_key = config.get('OPENROUTER', 'API_KEY', fallback='your_api_key_here')
    
    if not api_key:
        logger.error("Error: Please configure a valid OpenRouter API key in config.ini")
        return None
    
    # Read prompt type from config
    prompt_type = config.get('REWRITER', 'PROMPT', fallback='finance').lower()
    
    try:
        # Call OpenRouter API
        logger.info(f"Starting text rewrite: {text_file}")
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek/deepseek-chat-v3-0324:free",
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
        
        # Check response status
        response.raise_for_status()
        
        # Get rewritten text
        rewritten_text = response.json()['choices'][0]['message']['content']
        
        # Build output path
        output_path = os.path.join(output_dir, f"{base_name}.md")
        
        # Save rewritten text
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(rewritten_text)
        
        logger.info(f"Text rewrite completed: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Text rewrite failed: {e}")
        return None