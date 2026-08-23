from telethon.sync import TelegramClient
from telethon import functions
from config import api_id,api_hash

client = TelegramClient('session_name',api_id,api_hash)



with client :

    for dialog in client.get_dialogs():
        if dialog.name == 'ACAD C':
            print("found it")
            print(type(dialog.entity))
            entity = dialog.entity

            result = client(functions.messages.GetForumTopicsRequest(
                    peer = entity,
                    offset_date = None,
                    offset_id= 0,
                    offset_topic = 0,
                    limit = 100
            ))

            for topics in result.topics:
                 print(topics.title, '-',topics.id)
            break

            
        
    


  

 



