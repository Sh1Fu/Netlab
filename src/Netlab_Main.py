import shutil
from os.path import exists
from urllib.request import HTTPDefaultErrorHandler

from src.Netlab_App import App
from src.Netlab_DownloadImage import DownloadImage
from src.Netlab_TakePrice import TakePrice
from src.Netlab_UploadFiles import ISPUpload


class Main(App):
    def __init__(self) -> None:
        super().__init__()
        self.PRICE_NAME = "first.xlsx"
        self.IMAGES_PRICE = "images.xlsx"
        self.AUTH_URL = "http://services.netlab.ru/rest/authentication/token.json?"
        self.creds = None
        self.default_price = TakePrice(self.AUTH_URL, self.PRICE_NAME, self.creds)

    def login(self) -> bool:
        '''
        Trying to login to the API using the entered data
        '''
        if self.creds is None:
            self.creds = self.auth()
        try:
            self.default_price.auth_token(creds=self.creds)
            if self.default_price.token is not None:
                return True
        except BaseException or HTTPDefaultErrorHandler:
            return False

    def price_update(self, PRICE_TYPE: int, with_images: bool) -> None:
        '''
        Only price function
        '''
        self.default_price.take_price(PRICE_TYPE)
        self.default_price.csv_save(
            f"./price_lists/{self.PRICE_NAME}") if with_images == 0 else None

    def price_with_images(self, PRICE_TYPE: int, with_images: bool) -> None:
        '''
        Price and image function
        '''
        im = DownloadImage(self.PRICE_NAME, creds=self.creds)
        if exists("./price_lists/price_update_tmp.csv") and exists("./images/"):
            im.images_zip()
            self.isp_upload(with_images)
            return None
        if not exists("./price_lists/first.xlsx"):
            self.price_update(PRICE_TYPE, with_images)
        im.xlsx_work()
        im.images_zip()
        self.default_price.csv_save(
            f"./price_lists/{self.IMAGES_PRICE}")
        self.isp_upload(with_images)

    def isp_upload(self, is_image: bool) -> None:
        '''
        Upload new price list via FTP connection
        '''
        isp_session = ISPUpload()
        isp_session.upload_price(
            "price_update_tmp.csv", is_image)

    def clean(self) -> None:
        '''
        Remove all files from price_lists and images dir if you want
        '''
        shutil.rmtree("./price_lists/")
        shutil.rmtree("./images/")
