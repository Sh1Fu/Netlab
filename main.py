from __future__ import print_function
from urllib.request import HTTPDefaultErrorHandler
from pyfiglet import Figlet
from src.Netlab_TakePrice import TakePrice
from src.Netlab_App import App
from os.path import exists


class Main(App):
    def __init__(self) -> None:
        super().__init__()
        self.PRICE_NAME = "first.xlsx"
        self.AUTH_URL = "http://services.netlab.ru/rest/authentication/token.json?"

    def login(self) -> tuple:
        '''
        Trying to login to the API using the entered data
        '''
        creds = self.auth()
        session = TakePrice(self.AUTH_URL,  self.PRICE_NAME)
        try:
            api_token = session.auth_token(creds=creds)[0]
            return (1, api_token)
        except BaseException or HTTPDefaultErrorHandler:
            print("Problmes with auth. Try again\n")
            return (0, None)

    def price_update(self, PRICE_TYPE: int, auth_token: str) -> None:
        '''
        Only price function
        '''
        price = TakePrice(self.AUTH_URL,  self.PRICE_NAME)
        price.take_price(PRICE_TYPE, auth_token)

    def price_with_images(self, PRICE_TYPE: int, auth_token: str) -> None:
        '''
        Price and image function
        '''
        from src.Netlab_DownloadImage import DownloadImage
        if not exists("./price_lists/first.xlsx"):
            self.price_update(PRICE_TYPE, auth_token)
        im = DownloadImage(auth_token, self.PRICE_NAME)
        im.xlsx_work()


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
        if continue_input == 'y':
            auth = res.login()
        else:
            print("[!] Ok, Have a nice day :<\n")
            exit()
    choice = res.main_choice()
    if choice['price'] == "Only default price":
        res.price_update(PRICE_TYPE, auth_token=auth[1])
    elif choice['price'] == "Default price with images":
        res.price_with_images(PRICE_TYPE, auth_token=auth[1])
    elif choice['price'] == "Only configuration price":
        PRICE_TYPE = 1
        res.price_update(PRICE_TYPE, auth_token=auth[1])


if __name__ == "__main__":
    main()
