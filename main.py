from __future__ import print_function
import sys
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
        self.default_price = TakePrice(self.AUTH_URL, self.PRICE_NAME, self.creds)

    def login(self) -> bool:
        '''
        Trying to login to the API using the entered data
        '''
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
        self.default_price.csv_save(
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


class CMDInput(Main):
    def __init__(self) -> None:
        super().__init__()

    def check_cmd_input(self) -> bool:
        return True if len(sys.argv) > 1 else False

    def help_info(self) -> None:
        print("Netlab price update script")
        print("Usage:")
        print("-u <username> => set username from Netlab API")
        print("-p <password> => set password to Netlab user")
        print(
            "-m {1,2,3} => set current working mode (1 - Only default price, 2 - Only configuration price, 3 - Price with images")
        print("Example: python3 crontab_task.py -u shifu -p pass -m 1")
        
    @check_cmd_input
    def parse_arguments(self) -> None:
        commands = {"-u": [0, ""], "-p": [0, ""], "-m": [0, ""]}
        for command in commands.keys():
            if command in sys.argv:
                if sys.argv[sys.argv.index(command) + 1] is not None and sys.argv[sys.argv.index(command) + 1] not in commands:
                    commands[command][0] = 1
                    commands[command][1] = sys.argv[sys.argv.index(
                        command) + 1]
        for value in commands.values():
            if(value[0] == 0):
                self.help_info()
                return
    

def main():
    PRICE_TYPE = 0
    Hello = Figlet(font='slant')
    print(Hello.renderText('Netlab'))
    res = Main()
    auth = res.login()
    continue_input = "y"
    while(auth is False):
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
