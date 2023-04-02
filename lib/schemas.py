import typing as t
from enum import Enum

from pydantic import BaseModel


class MediaType(Enum):
    voice = '.ogg'
    video = '.mov'
    document = ''
    photo = '.jpg'


class From(BaseModel):
    id: int
    username: str = None
    first_name: str = None
    last_name: str = None


class Chat(BaseModel):
    id: int


class Attachment(BaseModel):
    file_id: str
    file_size: int


class Message(BaseModel):
    text: str = None
    from_: From
    message_id: int
    date: int
    chat: Chat
    voice: Attachment = None
    video: Attachment = None
    document: Attachment = None
    photo: t.List[Attachment] = []

    @property
    def user(self):
        return self.from_.username if self.from_.username else f"{self.from_.first_name} {self.from_.last_name}"

    @property
    def attachment(self):
        for media in MediaType:
            attch = getattr(self, media.name)
            if isinstance(attch, list):
                return attch[-1]
            elif isinstance(attch, Attachment):
                return attch

    @property
    def media_type(self):
        for media in MediaType:
            if getattr(self, media.name):
                return media.value

    class Config:
        fields = {
            'from_': 'from'
        }


class FileInfo(BaseModel):
    file_path: str

    @property
    def filename(self):
        return self.file_path.split('/')[-1]


class TLGResponse(BaseModel):
    text: str
    reply_to_message_id: int = None
    reply_markup: dict = None
    parse_mode: t.Literal['MarkdownV2'] = None
