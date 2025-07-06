import requests
import logging
from configparser import ConfigParser
import os

def translate_to_english(text: str) -> str:
    """
    Translate Chinese text to English using OpenRouter API
    
    Args:
        text (str): Chinese text to translate
        
    Returns:
        str: Translated English text
    """
    # Load API key from config
    config = ConfigParser()
    config.read('config.ini')
    api_key = config.get('openrouter', 'api_key', fallback=None)
    
    if not api_key:
        logging.error("OpenRouter API key not found in config.ini")
        return text
        
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "google/gemma-7b-it:free",
        "messages": [
            {
                "role": "system",
                "content": "You are a professional translator. Translate the following Chinese text to natural English while preserving technical terms and proper nouns:"
            },
            {
                "role": "user",
                "content": text
            }
        ]
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        logging.error(f"Translation failed: {str(e)}")
        return text