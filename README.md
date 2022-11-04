# Netlab
A simple python script for working with Netlab API

Download source code

```
git clone https://github.com/Sh1Fu/Netlab.git
```

Create a venv and install the necessary dependencies:

```
python3 -m venv <venv_name>
source <venv_name>/bin/activate
pip3 install -r requirements.txt
```

Add your credentials to OS Environment Variable: [Useful Info](https://www.serverlab.ca/tutorials/linux/administration-linux/how-to-set-environment-variables-in-linux/)

Variable's names:

* FTP_USERNAME
* FTP_PASSWORD
* FTP_IP
* FTP_PORT
* SHOP_ADDR

## Command line usage

```
usage: main.py [-h] [-u U] [-p P] [-m {1,2,3}]

options:
  -h, --help         show this help message and exit
  -u U, -username U  <username> => set username from Netlab API
  -p P, -password P  <password> => set password to Netlab user
  -m {1,2,3}         mode => set current working mode (1 - Only default price, 2 - Only configuration price, 3 - Price with images)
  
```

## User usage

Run main.py from main directory
```
python3 main.py
```

* Write your API username form Netlab service
* Write your API password form Netlab service
* Choose one of the following options
  * Only default price
  * Only configuration price
  * Default price with images
  * Delete all previous price files
  
## Crontab task example

```bash
0 0 * * 1,3,5 cd /home/<user>/Netlab/ &&  /home/<user>/Netlab/venv/bin/python3 main.py -u <API_NAME> -p <API_PASSWD> -m 1
```

**Note**: Check and adjust the time on the machine
