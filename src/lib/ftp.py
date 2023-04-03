import logging
from ftplib import FTP

logger = logging.getLogger(__name__)


class FTPClient():

    def __init__(self, server: str, port: str, username: str, password: str, folder: str) -> None:
        self.server, self.port = server, port
        self.user, self.passwrd = username, password
        self.folder = folder

    def ftp_connect(self):
        ftp = FTP()
        ftp.set_pasv(True)
        ftp.connect(self.server, self.port)
        ftp.login(user=self.user, passwd=self.passwrd)
        return ftp

    def change_dir(self, ftp: FTP, path: str):
        for folder in path.split('/'):
            if folder not in ftp.nlst():
                ftp.mkd(folder)
            ftp.cwd(folder)

    def upload(self, path: str, filename: str, content: bytes):
        try:
            ftp = self.ftp_connect()

            ftp.cwd(self.folder)
            self.change_dir(ftp, path)
            ftp.storbinary(f'STOR {filename}', content)
            logger.info('Файл успешно загружен на FTP сервер')
        except Exception as err:
            logger.exception('Upload file error destination %s filename %s', path, filename)
            raise err
        finally:
            ftp.quit()
