import json
import logging
from http import HTTPStatus

from config import settings
from core.handlers import MSGHandler
from lib import ftp, telegram
from tests.data import messages

logger = logging.getLogger(__name__)


def process_event(event, _) -> dict:
    try:
        body = json.loads(event['body'])
    except Exception as err:
        logger.warning('error to parse message: %s', err)
        return {
            'statusCode': HTTPStatus.UNPROCESSABLE_ENTITY
        }
    logger.debug('Incoming message')
    logger.debug(body)
    MSGHandler(
        ftp.FTPClient(**settings.ftp.dict()),
        telegram.API(
            settings.telegram.endpoint,
            settings.telegram.token,
        ),
        settings.max_file_size,
    ).process(body)
    return {
        'statusCode': HTTPStatus.OK,
    }


def trigger_handler(event, _):
    messages = event.get('messages')
    if not messages:
        logger.warning('Список сообщений пуст.\n Body: %s', event)
        return {
            'statusCode': HTTPStatus.BAD_REQUEST,
            'body': 'The request could not be correctly parsed or empty'
        }
    for msg in messages:
        process_event(msg['details']['message']['body'], None)

    return {
        'statusCode': HTTPStatus.OK,
    }


if __name__ == '__main__':
    process_event(event={'body': json.dumps(messages.photo)}, _=None),
    process_event(event={'body': json.dumps(messages.video)}, _=None),
