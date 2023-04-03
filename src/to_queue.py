import base64
import json
import logging
from http import HTTPStatus

import boto3

from config import settings

logger = logging.getLogger(__name__)


def handler(event, _):
    if event.get('isBase64Encoded'):
        body = base64.b64decode(event.get('body')).decode("UTF-8")
    else:
        body = event.get('body')
    try:
        body = json.loads(body)
        logger.info('Got message: %s', body)
    except Exception:
        response = {
            'statusCode': HTTPStatus.OK,
            'body': 'The request could not be correctly parsed'
        }
        logger.warning(
            'The request could not be correctly parsed.\nEvent: %s \nBody request: %s \nResponse: %s',
            event,
            body,
            response)
        return response

    client = boto3.client(
        service_name='sqs',
        endpoint_url=settings.queue.endpoint_url,
        region_name=settings.queue.region_name,
        aws_access_key_id=settings.queue.sa_corebot_id,
        aws_secret_access_key=settings.queue.sa_corebot_secret,
    )
    try:
        client.send_message(
            QueueUrl=settings.queue.url,
            MessageBody=json.dumps(body),
            MessageGroupId='duplicates')
        logger.info('Saved to queue:{%s}', body)
        response = {
            'statusCode': HTTPStatus.OK
        }
    except Exception as e:
        logger.error('Could not send data to SQS. Error:\n %s \ndata:{%s}', e, body)
        response = {
            'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR,
            'body': 'Internal Server Error'
        }
    logger.info('Response: %s', response)
    return response
