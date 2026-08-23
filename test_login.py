from telethon.sync import TelegramClient
from config import api_id,api_hash

client = TelegramClient('session_name',api_id,api_hash)

with client :
    client.get_dialogs()

    for dialog in client.get_dialogs():
        print(dialog.name, '-',dialog.id) 
 