import json
import logging
from http import HTTPStatus
from time import sleep

import boto3

from config import settings
from core.handlers import MSGHandler
from lib import ftp, telegram

logger = logging.getLogger(__name__)


def process_event(body) -> dict:
    try:
        body = json.loads(body)
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


def cloud_function_handler(event, _):
    logger.debug('Incoming message')
    logger.debug(event)
    process_event(event['body'])


def trigger_handler(event, _):
    messages = event.get('messages')
    if not messages:
        logger.warning('Список сообщений пуст.\n Body: %s', event)
        return {
            'statusCode': HTTPStatus.BAD_REQUEST,
            'body': 'The request could not be correctly parsed or empty'
        }
    for msg in messages:
        process_event(msg['details']['message'], None)

    return {
        'statusCode': HTTPStatus.OK,
    }


def process_message_queue():
    client = boto3.client(
        service_name='sqs',
        endpoint_url=settings.queue.url,
        region_name=settings.queue.region_name,
        aws_access_key_id=settings.queue.sa_corebot_id,
        aws_secret_access_key=settings.queue.sa_corebot_secret,
    )

    while True:
        messages = client.receive_message(
            QueueUrl=settings.queue.url,
            MaxNumberOfMessages=10,
        ).get('Messages', [])

        for msg in messages:
            logger.debug('The new message: %s', msg)

            try:
                client.delete_message(
                    QueueUrl=settings.queue.url,
                    ReceiptHandle=msg.get('ReceiptHandle')
                )
                logger.debug('Successfully deleted message by receipt handle %s', msg.get('ReceiptHandle'))
            except Exception as err:
                logger.error('Queue error %s during deleting the message: %s', err, msg.get('ReceiptHandle'))

            try:
                process_event(msg['Body'])
            except Exception:
                logger.exception('Error handle message %s', msg)
                
        if not messages:
            logger.debug('The QUEUE is empty. Queue url: %s', settings.queue.url)
            sleep(settings.check_queue_interval)


if __name__ == '__main__':
    process_message_queue()
