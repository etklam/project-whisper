import requests
import configparser
import os

def rewrite_text(text_file, output_dir="output/rewritten", input_name=None):
    """Rewrite text file using OpenRouter API and save result
    
    Args:
        text_file (str): Path to text file to rewrite
        output_dir (str): Output directory (default: 'output/rewritten')
        input_name (str): Original input filename (for output naming)
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract base name from input file
    if input_name:
        base_name = os.path.splitext(os.path.basename(input_name))[0]
    else:
        base_name = os.path.splitext(os.path.basename(text_file))[0]
    
    # Read text file content
    try:
        with open(text_file, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"Failed to read text file: {e}")
        return None
    
    # Read API key from config
    config = configparser.ConfigParser()
    config.read('config.ini')
    api_key = config.get('OPENROUTER', 'API_KEY')
    
    if not api_key or api_key == 'your_api_key_here':
        print("Error: Please configure valid OpenRouter API key in config.ini")
        return None
    
    try:
        # Call OpenRouter API
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek/deepseek-r1-0528:free",  # Default model
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一位專業的文本編輯助手，以港式粵語及繁體中文，請將以下文本改寫得更流暢、專業且易於理解，保持原意不變，目標是令十歲小孩能理解，並使用 markdown 格式輸出:"
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
        
        return output_path
    except Exception as e:
        print(f"Text rewriting failed: {e}")
        return None