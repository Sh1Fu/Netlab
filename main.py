from __future__ import print_function

import sys
import argparse
from pyfiglet import Figlet

from src.Netlab_Main import Main


class CMDInput(Main):
    def __init__(self) -> None:
        self.commands = {
            "-u": [0, ""], 
            "-p": [0, ""], 
            "-m": [0, ""]
        }
        self.function_def = {
            1: 'price_update',
            2: 'price_update',
            3: 'price_with_images'
        }
        super().__init__()

    def check_cmd_input(self) -> bool:
        return True if len(sys.argv) > 2 else False

    def help_info(self) -> None:
        print("Netlab price update script(command line arguments)")
        print("Usage:")
        print("-u <username> => set username from Netlab API")
        print("-p <password> => set password to Netlab user")
        print(
            "-m {1,2,3} => set current working mode (1 - Only default price, 2 - Only configuration price, 3 - Price with images")
        print("Example: python3 crontab_task.py -u shifu -p pass -m 1")
        
    def parse_arguments(self) -> dict:
        '''
        Take arguments from command line and parse them in to class dictionary
        '''
        keys = self.commands.keys()
        for command in keys:
            prog_argument = sys.argv[sys.argv.index(command) + 1]
            if (prog_argument not in keys and prog_argument is not None):
                self.commands[command][0], self.commands[command][1] = 1, prog_argument
            else:
                self.help_info()
                exit()
        return {'username': self.commands['-u'][1], 'password': self.commands['-p'][1]}
    
    def call(self) -> None:
        mode = int(self.commands['-m'][1])
        func = getattr(globals()["Main"](), self.function_def[mode])
        if mode != 2:
            if mode != 3:
                func(0, 0)
            else:
                func(0, 1)
        else:
            func(1, 0)


def main():
    print(Figlet(font='slant').renderText('Netlab'))
    PRICE_TYPE = 0
    CONTINUE_INPUT = "y"
    result_object = CMDInput() 
    command_args = result_object.check_cmd_input()
    if not command_args:
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
    if command_args:
        result_object.parse_arguments()
        result_object.call()
    else:
        choice = result_object.main_choice()
        if choice['price'] == "Only default price":
            result_object.price_update(PRICE_TYPE, 0)
            result_object.isp_upload(0)
        elif choice['price'] == "Default price with images":
            result_object.price_with_images(PRICE_TYPE, 1)
        elif choice['price'] == "Only configuration price":
            PRICE_TYPE = 1
            result_object.price_update(PRICE_TYPE, 0)
        elif choice['price'] == "Delete all previous price files":
            result_object.clean()
    


if __name__ == "__main__":
    main()
