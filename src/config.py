import logging.config

from pydantic import BaseSettings

from lib.logger import LOGGING


class Queue(BaseSettings):
    sa_corebot_id: str
    sa_corebot_secret: str
    endpoint_url: str = 'https://message-queue.api.cloud.yandex.net'
    url: str
    region_name: str = 'ru-central1'

    class Config:
        env_prefix = 'QUEUE_'
        env_file = '.env'


class FTP(BaseSettings):
    server: str
    port: int
    username: str
    password: str
    folder: str = 'Volume_2'

    class Config:
        env_prefix = 'FTP_'
        env_file = '.env'


class Telegram(BaseSettings):
    endpoint: str = 'https://api.telegram.org'
    token: str

    class Config:
        env_prefix = 'telegram_'
        env_file = '.env'


class Settings(BaseSettings):
    telegram = Telegram()
    ftp = FTP()
    queue = Queue()
    max_file_size: int = 1024**10
    check_queue_interval: int = 10


settings = Settings()

logging.config.dictConfig(LOGGING)
logging.getLogger('botocore').setLevel(logging.CRITICAL)
