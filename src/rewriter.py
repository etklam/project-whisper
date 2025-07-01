import requests
import configparser
import os

def rewrite_text(text_file, output_dir="output/rewritten", input_name=None):
    """使用OpenRouter API重写文本文件并保存结果
    
    Args:
        text_file (str): 要重写的文本文件路径
        output_dir (str): 输出目录，默认为 'output/rewritten'
        input_name (str): 原始输入文件名（用于生成输出文件名）
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 从输入文件名中提取基础名称（不含扩展名）
    if input_name:
        base_name = os.path.splitext(os.path.basename(input_name))[0]
    else:
        base_name = os.path.splitext(os.path.basename(text_file))[0]
    
    # 读取文本文件内容
    try:
        with open(text_file, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"读取文本文件失败: {e}")
        return None
    
    # 读取配置文件获取API密钥
    config = configparser.ConfigParser()
    config.read('config.ini')
    api_key = config.get('OPENROUTER', 'API_KEY')
    
    if not api_key or api_key == 'your_api_key_here':
        print("错误: 请在config.ini中配置有效的OpenRouter API密钥")
        return None
    
    try:
        # 调用OpenRouter API
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek/deepseek-r1-0528:free",  # 默认模型
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
        
        # 检查响应状态
        response.raise_for_status()
        
        # 获取重写后的文本
        rewritten_text = response.json()['choices'][0]['message']['content']
        
        # 构建输出文件路径
        output_path = os.path.join(output_dir, f"{base_name}.md")
        
        # 保存重写结果
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(rewritten_text)
        
        return output_path
    except Exception as e:
        print(f"文本重写失败: {e}")
        return None