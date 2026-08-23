from telethon import TelegramClient, functions
import json
import os
import subprocess
from config import api_id,api_hash


client = TelegramClient('session_name', api_id, api_hash)

LOG_FILE = 'downloaded_log.json'


def load_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            content = f.read().strip()
            if content:
                return json.loads(content)
    return {}


def save_log(log):
    with open(LOG_FILE, 'w') as f:
        json.dump(log, f, indent=2)


async def get_group_entity(client, group_name):
    async for dialog in client.iter_dialogs():
        if dialog.name == group_name:
            return dialog.entity
    return None


async def get_topics(client, entity):
    result = await client(functions.messages.GetForumTopicsRequest(
        peer=entity,
        offset_date=None,
        offset_id=0,
        offset_topic=0,
        limit=100
    ))
    return result.topics

def convert_folder_to_pdf(folder_path):
    converted_count = 0
    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path,filename)
        if filename.lower().endswith('.pdf'):
            continue

        result = subprocess.run([
            r'C:\Program Files\LibreOffice\program\soffice.exe', '--headless', '--convert-to', 'pdf',
            '--outdir', folder_path, filepath
        ], capture_output=True, text=True)

        if result.returncode == 0:
            os.remove(filepath)
            converted_count +=1
        else :
            print(f"failed to convert {filename} : {result.stderr}")
    return converted_count

async def sync_topic(client, entity, topic_id, topic_name, log):
    if topic_name not in log:
        log[topic_name] = []

    desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop','Telegram Downloads')
    folder = os.path.join(desktop_path, topic_name)
    os.makedirs(folder, exist_ok=True)

    messages = await client.get_messages(entity, reply_to=topic_id, limit=None)

    new_downloads = 0
    for message in messages:
        allowed_extensions = ('.pdf','.docx','.doc','.pptx','.ppt','.xlsx','xls','.txt','.odt','.rtf','.csv')
        if message.file and message.file.name and message.file.name.lower().endswith(allowed_extensions):
            if message.id not in log[topic_name]:
                print(f"Downloading: {message.file.name}")
                await message.download_media(file=folder + '/')
                log[topic_name].append(message.id)
                new_downloads += 1
    return new_downloads