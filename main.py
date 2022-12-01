from __future__ import print_function

from argparse import ArgumentParser
import shutil
import sys
from os.path import exists
from typing import Any
from urllib.request import HTTPDefaultErrorHandler
from pyfiglet import Figlet

from src.Netlab_App import App
from src.Netlab_DownloadImage import DownloadImage
from src.Netlab_TakePrice import TakePrice
from src.Netlab_UploadFiles import ISPUpload


def check_cmd_input(function_name) -> None:
    def wrapper(self):
        function_name(self) if len(sys.argv) > 1 else None
    return wrapper


class Main(App):
    def __init__(self) -> None:
        super().__init__()
        self.AUTH_URL = "http://services.netlab.ru/rest/authentication/token.json?"
        self.PRICE_NAME = "first.xlsx"
        self.IMAGES_PRICE = "images.xlsx"
        self.IS_PROXY = False
        self.creds = None
        self.mode = 0
        self.default_price = TakePrice(
            self.AUTH_URL, self.PRICE_NAME)
        self.function_def = {
            1: 'price_update',
            2: 'price_update',
            3: 'price_with_images',
            4: 'price_update'
        }
        self.prog_args = ArgumentParser()

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

    @check_cmd_input
    def parse_aruments(self) -> None:
        '''
        Work with command line arguments if we need to set up new cron task
        '''
        self.prog_args.add_argument(
            '-u', '-username', help='<username> => set username from Netlab API', type=str)
        self.prog_args.add_argument(
            '-p', '-password', help='<password> => set password to Netlab user', type=str)
        self.prog_args.add_argument(
            '-m', help='mode => set current working mode (1 - Only default price, 2 - Only configuration price, 3 - Price with images)', type=int, choices=[1, 2, 3, 4])
        self.prog_args.add_argument(
            '--proxy', help="Use proxy while images are finding", action='store_true')

    def configure_settings(self) -> None:
        '''
        Update ``self.creds`` dictionary with credentials form cmd args\n
        Init working mode ``self.mode``
        '''
        self.parse_aruments()
        args = self.prog_args.parse_args()
        self.mode = args.m
        self.creds = {'username': args.u, 'password': args.p}
        if args.proxy:
            self.IS_PROXY = True

    def call(self) -> None:
        '''
        We call the function we need depending on the selected mode of operation.\n
        The choice goes through the -m option in the command line arguments
        '''
        func = getattr(locals()["self"], self.function_def[self.mode])
        if self.mode != 2:
            if self.mode != 3:
                func(0, 0)
            else:
                func(0, 1)
        else:
            func(1, 0)

    def choice(self) -> None:
        choice = self.main_choice()
        if choice['price'] == "Only configuration price":
            self.price_update(1, 0)
        if choice['price'] == "Default price with images":
            self.price_with_images(0, 1)
        if choice['price'] == "Delete all previous price files":
            self.clean()
        if choice['price'] == "Only default price" or choice['price'] == "Default price and Pandas frame":
            self.price_update(0, 0)
            self.isp_upload(0)

    def price_update(self, PRICE_TYPE: int, with_images: bool) -> None or Any:
        '''
        Only price function\n
        Update price list from Netlab service and save it as csv file with specific options
        '''
        self.default_price.take_price(PRICE_TYPE, self.mode)
        self.default_price.csv_save(
            f"./price_lists/{self.PRICE_NAME}") if with_images == 0 else None
        if self.mode == 4:
            return self.default_price.format_pandas()

    def price_with_images(self, PRICE_TYPE: int, with_images: bool) -> None:
        '''
        Price and image function\n
        Update price list and then download all required images. After all, files are sent via FTP to the server
        '''
        im = DownloadImage(self.PRICE_NAME, creds=self.creds)
        if exists("./price_lists/price_update_tmp.csv") and exists("./images/"):
            im.images_zip()
            self.isp_upload(with_images)
            return None
        if not exists("./price_lists/first.xlsx"):
            self.price_update(PRICE_TYPE, with_images)
        im.xlsx_work(self.IS_PROXY)
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


def main():
    print(Figlet(font='slant').renderText('Netlab'))
    CONTINUE_INPUT = "y"
    result_object = Main()
    check_args = True if len(sys.argv) > 1 else False
    if check_args:
        result_object.configure_settings()
    auth_try = result_object.login()
    while(not auth_try):
        CONTINUE_INPUT = input(
            "[!] AuthError: Check your API credentials.\nContinue? Type [y]/n: ")
        if CONTINUE_INPUT == 'n':
            print("[!] Ok, Have a nice day :<\n")
            exit()
        else:
            result_object.creds = None
            auth_try = result_object.login()
    if check_args:
        result_object.call()
    else:
        result_object.choice()


if __name__ == "__main__":
    main()
