# Telegram bot backend to download incoming attachments to FTP server. # 

Settings in .env.example file.

Use Serverless Yandex Cloed Queue (like AWS) to implement message brocker for storing Telegram API messages before loading to FTP.

Enter point for storing messages to queue - to_queue.handler
Enter point for the loading part:
- main.trigger_handler - if Ya Cloud Queue Trigger is used
- main.cloud_function_handler - if direct message sending (without queue) 
- main.process_message_queue - if the loader retrieves messages from the queue itself 
