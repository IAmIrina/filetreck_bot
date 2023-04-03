import json
import logging
import types
from contextlib import contextmanager

import requests

from lib import schemas

logger = logging.getLogger(__name__)


class API():

    HEADERS = types.MappingProxyType({'Content-Type': 'application/json'})

    def __init__(self, endpoint: str, token: str) -> None:
        self.url = f"{endpoint}/bot{token}"
        self.attachment_url = f'{endpoint}/file/bot{token}'

    def send_message(self, chat_id: int, **kwargs) -> None:
        payload = dict(
            chat_id=chat_id,
            **kwargs,
        )
        response = requests.post(
            f"{self.url}/sendMessage",
            headers=self.HEADERS,
            data=json.dumps(payload)
        )
        try:
            response.raise_for_status()
        except Exception as err:
            logger.error(response.text)
            raise err

    def get_file_info(self, file_id: str) -> schemas.FileInfo:
        payload = {'file_id': file_id}
        response = requests.get(
            f"{self.url}/getFile",
            params=payload,
        ).json()
        return schemas.FileInfo(**response['result'])

    class Reader():
        def __init__(self, response: requests.Response) -> None:
            self.response = response

        def read(self, chunk_size: int):
            for chunk in self.response.iter_content(chunk_size=chunk_size):
                return chunk

    @contextmanager
    def download_file(self, file_path: str) -> bytes:
        with requests.get(f"{self.attachment_url}/{file_path}", stream=True) as response:
            response.raise_for_status()
            yield self.Reader(response)
