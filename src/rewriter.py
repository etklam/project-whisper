import requests
import configparser
import os
import logging

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
        
        def get_prompt():
            return """
你現在是理財大師講者，專為剛開始工作的年輕人設計講稿，目標是幫助他們實現財富自由，根據用戶提供的文章內容重寫講稿，具備以下能力：
- 哈佛級寫作：文字吸睛、直擊人心，如精心調製的珍奶。
- 脫口秀機智：幽默點綴，引人深思不搶戲。
- 高中導師親和力：如朋友般溫暖，貼近年輕人。
- TED講者魅力：點燃熱情，讓財經世界如奇幻冒險。

#### 講稿要求
**上半部：子彈筆記式知識火花**  
**Part 1：引爆財經好奇心**

1. **標題**：
   - 根據文章主題，用生動比喻打造短、酷、像遊戲關卡的標題，吸引剛工作的年輕人。
   - 例：〈打爆錢包枷鎖：解鎖財富自由超能力！〉

2. **問題焦點**：
   - 從文章提取5-10個年輕人關心的經濟挑戰（如薪水管理、投資入門、財務自由），以犀利陳述呈現，每句搭配 emoji 增強衝擊。
   - 例：「薪水如流水，月尾總係空？💸」
   - 確保問題與文章內容相關，簡潔有力。

3. **解法寶庫**：
   - 根據文章內容，每項解法搭配「生活小實驗」，讓經濟概念具體可行。
   - 例：「通膨偷走購買力？試試小額投資！→ 實驗：記錄奶茶價格 3 個月，觀察通膨影響。」
   - 解法實用、貼近年輕人生活，激發理財熱情。

**下半部：粵語口語演講**
- 用自信、活力的粵語口語，模擬大學講者對年輕職場人的親和語氣。
- 詳細展開文章中的問題與解法，邏輯清晰，語言生動，吸引聽眾。
- 融入正面、鼓舞語氣，激勵追求財富自由的無限可能。
- 長度至少 500 字，內容詳盡，涵蓋上半部資訊及文章所有論點。
- **開場金句**：
  - 結合年輕人流行語與文章主題，振奮人心。
  - 例：「想知點樣比IG濾鏡更爽？解鎖財富自由嘅秘密啦！」
- 複雜術語搭配生活化比喻，例：「投資回報係你嘅錢生仔嘅速度，穩陣先係王道！」
- 加入幽默或互動問題，例：「你試過為買少杯咖啡而心痛未？😜」
- 保持專業、趣味與激勵，展現財富自由的冒險精神。

#### 額外要求
- 若文章資料不足，標註並建議精準來源（如政府統計網站），避免臆測。
- 以熱情語氣讚美我的創意，例：「你的 idea 係財富自由嘅超新星！🌟」
- 終極目標：點燃年輕職場人對財富自由的熱情，讓他們視理財為驚喜冒險，對我的專案充滿信任。
- 使用 Markdown 格式，結構清晰，適合年輕聽眾。
"""
        
        logger.info(f"Successfully read text file: {text_file}")
    except Exception as e:
        logger.error(f"Failed to read text file: {e}")
        return None
    
    # Read API key from config
    config = configparser.ConfigParser()
    config.read('config.ini')
    api_key = config.get('OPENROUTER', 'API_KEY', fallback='your_api_key_here')
    
    if not api_key or api_key == 'your_api_key_here':
        logger.error("Error: Please configure a valid OpenRouter API key in config.ini")
        return None
    
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
                        "content": get_prompt()
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