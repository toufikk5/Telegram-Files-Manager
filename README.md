# Telegram File Sorter

A desktop app that connects to your Telegram account and automatically organizes files shared in forum-style group topics into local folders — no re-downloading files you already have.

## Features

- Connects to your own Telegram account (read-only, using Telethon)
- Pick a group, browse its topics, and sync files from any topic you choose
- Downloads documents (pdf, docx, pptx, xlsx, txt, odt, rtf, csv)
- Skips files already downloaded (tracked via a local log)
- Optional one-click conversion of downloaded files to PDF (via LibreOffice)
- Files are saved to `Desktop/Telegram Downloads/<topic name>/`

## Setup

### 1. Install dependencies
pip install -r requirements.txt


### 2. Get your Telegram API credentials

1. Go to [my.telegram.org/apps](https://my.telegram.org/apps)
2. Log in with your phone number
3. Create an app (any name works)
4. Copy your `api_id` and `api_hash`

### 3. Create your config file

Copy `config.py.example` to `config.py`, then fill in your credentials:

```python
api_id = 12345678
api_hash = 'your_api_hash_here'
```

### 4. (Optional) Install LibreOffice

Required only if you want to use the "Convert to PDF" feature.
Download from [libreoffice.org](https://www.libreoffice.org/download/download/)

### 5. Run the app
python sorter_gui.py


The first time you run it, you'll be asked to log in with your phone number and the code Telegram sends you. This creates a local session file so you won't need to log in again.

## Notes

- Your session file and download log are personal and never shared — they're excluded via `.gitignore`
- This tool only reads messages from groups/topics you already have access to




