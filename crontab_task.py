import subprocess
import sys
from typing import Any
import keyboard
from time import sleep
# Prov arguments
# python3 crontab_task.py -u <username> -p <password> -m {1,2,3}
#          argv[0]     argv[1] argv[2] argv[3] argv[4] argv[5] argv[6]


class CronTab:
    def __init__(self) -> None:
        pass

    def help_info(self) -> None:
        print("Netlab price update script")
        print("Usage:")
        print("-u <username> => set username from Netlab API")
        print("-p <password> => set password to Netlab user")
        print(
            "-m {1,2,3} => set current working mode (1 - Only default price, 2 - Only configuration price, 3 - Price with images")
        print("Example: python3 crontab_task.py -u shifu -p pass -m 1")

    def check_args(self) -> None:
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
        self.run_netlab(
            username=commands["-u"][1], password=commands["-p"][1], mode=commands["-m"][1])

    def run_netlab(self, username: str, password: str, mode: str) -> None:
        process = subprocess.Popen(["python3", "main.py"])
        sleep(20)
        process.communicate(input=("%s\n%s\n" % (username, password)).encode())
        for count in range(int(mode) - 1):
            keyboard.send("page down")
        keyboard.send("enter")


def main():
    cron = CronTab()
    cron.check_args()


if __name__ == "__main__":
    main()
