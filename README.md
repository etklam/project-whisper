# Project Whisper

Project Whisper 是一個用於音頻處理的 Python 項目，旨在提供音頻下載、清理、重寫與轉錄等功能。

## 目錄結構

```
.
├── .gitignore
├── README.md
├── development-plan.md
├── main.py
├── requirements.txt
├── input/
│   └── (音頻處理的輸入文件)
├── src/
│   ├── cleaner.py       # 音頻清理功能
│   ├── downloader.py    # 音頻下載功能
│   ├── rewriter.py      # 音頻重寫功能
│   ├── transcriber.py   # 音頻轉錄功能
│   └── utils.py         # 公用實用函數
├── whisper/
│   └── (主要的音頻處理邏輯)
```

## 安裝

請按照以下步驟安裝項目所需的依賴：

```bash
# 克隆該項目
git clone https://example.com/project-whisper.git

# 進入項目目錄
cd project-whisper

# 創建虛擬環境 (可選，但推薦)
python3 -m venv venv

# 激活虛擬環境
# Windows:
# venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安裝依賴
pip install -r requirements.txt
```

## 使用方法

以下是如何使用此專案的基本指南。

### 下載音頻

使用 downloader.py 下載音頻：

```bash
python src/downloader.py --url <音頻文件的URL>
```

### 清理音頻

使用 cleaner.py 清理音頻：

```bash
python src/cleaner.py --input <輸入音頻文件的路徑> --output <輸出音頻文件的路徑>
```

### 重寫音頻

使用 rewriter.py 重寫音頻：

```bash
python src/rewriter.py --input <輸入音頻文件的路徑> --output <輸出音頻文件的路徑>
```

### 轉錄音頻

使用 transcriber.py 進行轉錄：

```bash
python src/transcriber.py --input <輸入音頻文件的路徑> --output <輸出文本文件的路徑>
```

## 貢獻指南

歡迎任何形式的貢獻！請查看 [development-plan.md](development-plan.md) 以了解當前的開發計劃。

## 許可證

此項目根據 [MIT 許可證](LICENSE) 發布。