from typing import Any
from requests import get
from json import loads
import xml.etree.ElementTree as ET
from openpyxl import Workbook
from Netlab_UpdatePrice import UpdatePrice
from tqdm import tqdm
from time import sleep


class TakePrice(UpdatePrice):
    def __init__(self, auth_url: str, file_name: str) -> None:
        self.auth_url = auth_url
        self.file_name = file_name
        self.diction = dict()
        self.current_row = 1
        super().__init__(file_name=self.file_name)

    def auth_token(self, creds: Any) -> tuple:
        '''
        API function. Take token from Netlab API\n
        ``creds`` - actual json credential data\n
        Return value: tuple
        * ``token`` - API token
        * ``live_time`` - raw time of token live
        '''
        req = get(self.auth_url, creds)
        data_json = self.prepare_json(req.text)
        token, live_time = data_json["tokenResponse"]["data"]["token"], data_json["tokenResponse"]["data"]["expiredIn"]
        return (token, live_time)

    def prepare_json(self, data: str) -> Any:
        '''
        Transform response from Netlab to Python dict
        '''
        return loads(data[data.find("& {") + 2:])

    def usd(self) -> float:
        '''
        Return current usd/rub value from CBR api
        '''
        response = get("https://www.cbr.ru/scripts/XML_daily.asp")
        usd_rate = float(ET.fromstring(response.text).find("./Valute[CharCode='USD']/Value").text.replace(",", "."))
        return usd_rate

    def parse_time(self, time: str) -> Any:
        pass

    def catalog_names(self, token) -> Any:
        '''
        API function. Take catalog (json object) from Netlab API. (catalog.json file)
        '''
        data = get("http://services.netlab.ru/rest/catalogsZip/Прайс-лист.json?oauth_token=%s" % token)
        data_json = self.prepare_json(data.text)
        return data_json

    def find_name(self, json_object: list, id: str) -> str:
        return [obj for obj in json_object if obj['id'] == id][0]['name']

    def take_price(self, PRICE_TYPE: int, token: str) -> None:
        '''
        API function. Take all products from category.
        '''
        self.diction = self.update_list(self.diction)
        catalog_json = self.catalog_names(token)
        wb = Workbook()
        active_sheet = wb.active
        self.init_default_xlsx(active_sheet=active_sheet) if PRICE_TYPE == 0 else self.init_main_xlsx(active_sheet=active_sheet)
        for subcatalog in tqdm(catalog_json["catalogResponse"]["data"]["category"]):
            if subcatalog["name"] != "Услуги и Получи!Фонд":
                products = get("http://services.netlab.ru/rest/catalogsZip/Прайс-лист/%s.json?oauth_token=%s" % (subcatalog["id"], token))
                products = self.prepare_json(products.text)
                try:
                    self.product_take(PRICE_TYPE, products['categoryResponse']['data']['goods'], active_sheet, subcatalog["id"])
                except BaseException as e:
                    print('\nError: ' + e + '\n')
                    wb.save(self.file_name)
            else:
                continue
            sleep(0.3)
        wb.save(self.file_name)