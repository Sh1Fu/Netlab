from __future__ import print_function

import shutil
from os import remove
from os.path import exists
from urllib.request import HTTPDefaultErrorHandler

from pyfiglet import Figlet

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

    def login(self) -> tuple:
        '''
        Trying to login to the API using the entered data
        '''
        self.creds = self.auth()
        session = TakePrice(self.AUTH_URL,  self.PRICE_NAME, self.creds)
        try:
            api_token = session.auth_token(creds=self.creds)[0]
            if api_token != "":
                return (1, api_token)
        except BaseException or HTTPDefaultErrorHandler or api_token == "":
            return (0, None)

    def price_update(self, PRICE_TYPE: int, with_images: bool) -> None:
        '''
        Only price function
        '''
        price = TakePrice(self.AUTH_URL, self.PRICE_NAME, self.creds)
        price.take_price(PRICE_TYPE)
        price.csv_save(
            f"./price_lists/{self.PRICE_NAME}") if with_images == 0 else None

    def price_with_images(self, PRICE_TYPE: int) -> None:
        '''
        Price and image function
        '''
        im = DownloadImage(self.PRICE_NAME, creds=self.creds)
        if exists("./price_lists/price_update_tmp.csv") and exists("./images/"):
            im.images_zip()
            self.isp_upload(1)
            return None
        if not exists("./price_lists/first.xlsx"):
            self.price_update(PRICE_TYPE, 1)
        im.xlsx_work()
        im.images_zip()
        TakePrice(self.AUTH_URL, self.PRICE_NAME, self.creds).csv_save(
            f"./price_lists/{self.IMAGES_PRICE}")
        self.isp_upload(1)

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


def main():
    PRICE_TYPE = 0
    Hello = Figlet(font='slant')
    print(Hello.renderText('Netlab price update'))
    res = Main()
    auth = res.login()
    continue_input = "y"
    while(auth[0] != 1):
        continue_input = input(
            "[!] AuthError: Check your API credentials.\nContinue? Type [y]/n: ")
        if continue_input == 'n':
            print("[!] Ok, Have a nice day :<\n")
            exit()
        else:
            auth = res.login()
    choice = res.main_choice()
    if choice['price'] == "Only default price":
        res.price_update(PRICE_TYPE, 0)
        res.isp_upload(0)
    elif choice['price'] == "Default price with images":
        res.price_with_images(PRICE_TYPE)
    elif choice['price'] == "Only configuration price":
        PRICE_TYPE = 1
        res.price_update(PRICE_TYPE, 0)
    elif choice['price'] == "Delete all previous price files":
        res.clean()


if __name__ == "__main__":
    main()
