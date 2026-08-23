from telethon.sync import TelegramClient
from config import api_id,api_hash

client = TelegramClient('session_name',api_id,api_hash)

ARCHI_TOPIC_ID = 13
with client :
    entity = None
    for dialog in client.get_dialogs():
        if dialog.name == 'ACAD C':
            entity = dialog.entity
            break
    messages = client.get_messages(entity, reply_to = ARCHI_TOPIC_ID, limit = None)

    for message in messages:
        if message.file and message.file.name and message.file.name.endswith('.pdf'):
          print(f"Downloading: {message.file.name}")
          message.download_media(file='downloads/')
    print("all done")