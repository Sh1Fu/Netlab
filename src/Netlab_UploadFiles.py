import os
import ftplib
import logging
from time import strftime
from typing import Any
from threading import Thread


class TransferError(Exception):
    '''
    Specific Error class to logging into file. Checks if my file is uploaded to server
    '''

    def __init__(self, file_name: str) -> None:
        self.file_name = file_name

    def __str__(self) -> str:
        return (f"File {self.file_name} is not uploaded in server")


class ISPUpload:
    def __init__(self) -> None:
        self.LOG_FILE = "./out/%s.log" % strftime("%Y%m%d-%H%M")
        self.ip = os.environ["FTP_IP"]
        self.port = os.environ["FTP_PORT"] if os.environ["FTP_PORT"] else "21"
        self.username = os.environ["FTP_USERNAME"]
        self.password = os.environ["FTP_PASSWORD"]
        self.shop_addr = os.environ["SHOP_ADDR"]
        logging.basicConfig(filename=self.LOG_FILE, level=logging.DEBUG,
                            format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        logging.debug("[+] Start FTP Connection..\n")
        self.ftp_info = self.check_ftp_connection()

    def check_ftp_connection(self) -> tuple:
        '''
        Try to create a new FTP connection thanks to send the NOOP command. All creds are in Env Variables
        Return value - tuple with next variables: ``New FTP Connection variable`` and ``Status Code(0 or 1)``\n
        If ``Status Code`` - 0 then ``New FTP Connections`` - None
        '''
        ftp_session = ftplib.FTP(host=self.ip)
        try:
            ftp_session.connect()
            ftp_session.login(user=self.username, passwd=self.password)
            ftp_session.voidcmd("NOOP")
            return (ftp_session, 1)
        except IOError as e:
            logging.exception(msg=f"IOError: {str(e)}")
        except ftplib.error_perm:
            logging.exception(msg="(HTTP 500-599 Error on FTP server)")
        except ftplib.error_temp:
            logging.exception(msg="(HTTP 400-499) Error on FTP server")
        return(None, 0)

    def max_del(self, max_iteration: int) -> int:
        mxDel = 0
        for i in range(max_iteration, 1, -1):
            if max_iteration % i == 0 and i >= mxDel and (max_iteration / i > 5 and max_iteration / i < 8):
                mxDel = i
                return mxDel

    def thread_upload(self) -> None:
        '''
        Take a new ftp_connection and upload ``count`` files via new thread\n
        ``count`` - count of uploading files\n
        ``ftp_conn`` - new ftp connection\n
        '''
        count_of_files = os.listdir("./images/")
        thread_count_files = self.max_del(count_of_files)
        count_of_threads = count_of_files / thread_count_files
        for i in range(count_of_threads):
            new_ftp = self.check_ftp_connection()[0]
            new_thread = Thread(target=self.images_upload,
                                args=(new_ftp, thread_count_files * i, thread_count_files * (i + 1)))
            new_thread.start()
            new_ftp.close()

    def upload_price(self, file_name: str, with_images: bool) -> None:
        '''
        Upload function. Try to upload our new price or image file.\n
        ``file_name`` - name of our file\n
        ``with_images`` - Boolean flag to images_upload. If this flag is True - we start to upload image dir to server\n
        '''
        try:
            if self.ftp_info[1] == 1:
                self.ftp_info[0].cwd(f"./www/{self.shop_addr}/upload/")
                if file_name in self.ftp_info[0].nlst():
                    self.ftp_info[0].delete(file_name)
                    msg = f"Info: old {file_name} has been successfully deleted"
                    logging.log(msg=msg, level=logging.INFO)
                    print
                price = open(f"./price_lists/{file_name}", "rb")
                self.ftp_info[0].storbinary(f"STOR {file_name}", price)
                price.close()
                if file_name in self.ftp_info[0].nlst():
                    if with_images:
                        logging.log(
                            msg=f"Info: Upload images to ftp server", level=logging.INFO)
                        # self.images_upload(ftp_conn=self.ftp_info[0])
                        self.thread_upload()
                    self.ftp_info[0].close()
                else:
                    raise TransferError(file_name=file_name)
        except ftplib.error_reply:
            logging.exception(msg="Unexpected reply from server")

    def images_upload(self, ftp_conn: Any, start_index: int, end_index: int) -> None:
        '''
        Images upload function. Create ``images`` dir if its not exists\n
        ``ftp_conn`` - our current FTP connection
        '''
        files = os.listdir("./images/")
        if "images" not in ftp_conn.nlst():
            ftp_conn.mkd("./images/")
        ftp_conn.cwd("./images/")
        for index in range(start_index, end_index, 1):
            image_file = open(f"./images/{files[index]}", 'rb')
            try:
                ftp_conn.storbinary(f"STOR {files[index]}", image_file)
                if files[index] not in ftp_conn.nlst():
                    logging.exception(msg=TransferError(files[index]))
            except ftplib.all_errors as e:
                logging.exception(f"FTPError: {str(e)}")
            image_file.close()
