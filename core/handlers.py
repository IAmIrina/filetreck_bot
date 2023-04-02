import logging
from datetime import datetime

from lib import ftp, messages, schemas, telegram

logger = logging.getLogger(__name__)


class MSGHandler():

    def __init__(
            self,
            ftp: ftp.FTPClient,
            bot: telegram.API,
            max_attachment_size: int = 1024**3
    ) -> None:
        self.ftp = ftp
        self.bot = bot
        self.max_attachment_size = max_attachment_size

    def _gen_filename(self, filename: str, message: schemas.Message) -> str:
        if len(filename.split('.')) == 1:
            filename += message.media_type
        return f"{message.message_id}_{filename}"

    def _gen_file_path(self, sender: str, sent_at: int) -> str:
        sent_at = datetime.fromtimestamp(sent_at).isoformat()[:7]
        return f"{sender.replace(' ','_')}/{sent_at}"

    def process(self, body: dict) -> None:
        try:
            message = schemas.Message(**body.get('message', {}))
        except Exception:
            logger.exception('Unable to parse message')
            return

        if not message.attachment:
            return

        if message.attachment.file_size > self.max_attachment_size:
            logger.warning(
                'The attachment file size too big: %s GB',
                message.attachment.file_size / 1024**3,
            )
            self.bot.send_message(
                chat_id=message.from_.id,
                **schemas.TLGResponse(
                    text=messages.TOO_BIG.format(self.max_attachment_size / 1024**2),
                    reply_to_message_id=message.message_id,
                ).dict(exclude_none=True),
            )
            return

        attachment = self.bot.get_file_info(message.attachment.file_id)

        with self.bot.download_file(attachment.file_path) as content:
            self.ftp.upload(
                path=self._gen_file_path(sender=message.user, sent_at=message.date),
                filename=self._gen_filename(filename=attachment.filename, message=message),
                content=content,
            )

        self.bot.send_message(
            chat_id=message.from_.id,
            **schemas.TLGResponse(
                text=messages.SAVED_TO_FTP,
                reply_to_message_id=message.message_id,
            ).dict(exclude_none=True),
        )
