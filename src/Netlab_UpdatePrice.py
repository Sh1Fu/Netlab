import pandas
from json import load
from typing import Any
from requests import get
import xml.etree.ElementTree as ET


class UpdatePrice:
    def __init__(self, file_name) -> None:
        self.goods = {}
        self.goods_len = 0
        self.file_name = file_name
        self.usd_value = self.usd()
        self.cmo = 0

    def usd(self) -> float:
        '''
        Return current usd/rub value from CBR api
        '''
        response = get("https://www.cbr.ru/scripts/XML_daily.asp")
        usd_rate = float(ET.fromstring(response.text).find(
            "./Valute[CharCode='USD']/Value").text.replace(",", "."))
        return usd_rate

    def update_list(self, cat: dict) -> dict:
        '''
        Loading custom margin from catalog.json file\n
        ``cat`` - blank list
        '''
        with open("catalog.json", "r", encoding="utf-8") as f:
            cat = load(f)
        return cat

    def pandas_config(self, product_data: dict, category: str) -> None:
        '''
        Take another product and add him in to dict of dicts.\n 
        This is for pandas array format\n
        ``product_data`` - json of current product\n
        ``category`` - name of current category\n
        ''' 
        if product_data['properties']['PN'] is not None:
            pandas_product = {
                "Категория": category,
                "Наименование": product_data['properties']['название'],
                "Производитель": product_data['properties']['производитель'] if product_data['properties']['производитель'] != "No name" else "Netlab",
                "Заводской номер": product_data['properties']['PN'],
                "Цена Netlab": product_data['properties']['цена по категории F'] * self.usd_value
            }
            self.goods[self.goods_len] = pandas_product
            self.goods_len += 1
    
    def format_pandas(self) -> Any:
        tmp_pandas = pandas.DataFrame.from_dict(self.goods, "index")
        tmp_pandas.reset_index(drop=True, inplace=True)
        return tmp_pandas

    def find_count(self, id: str, cat: dict) -> tuple:
        '''
        The main algorithmic function. Finds the required markup by changing the checked Id\n
        ``id`` - product id\n
        ``cat`` - dictionary from catalog.json file\n
        Return value: tuple\n
        * ``category_ids`` - list with all product categories
        * ``float value`` - product markup
        '''
        category_ids = list()
        index = 0
        tmp_index = 0
        try:
            while (cat['catalogResponse']['data']["category"][index]["id"] != id):
                index += 1
        except IndexError as e:
            print(f"{str(e)} at index {index}")
        current_dict = cat['catalogResponse']['data']["category"][index]
        category_ids.append(current_dict["id"])
        while (current_dict["parentId"] != "0" and int(current_dict["id"]) >= 30):
            tmp_index = 0
            try:
                while current_dict["parentId"] != cat['catalogResponse']['data']["category"][tmp_index]["id"] and tmp_index < len(cat['catalogResponse']['data']["category"]):
                    tmp_index += 1
            except BaseException:
                print(tmp_index, index, current_dict,
                      cat['catalogResponse']['data']["category"][tmp_index])
                break
            if current_dict['name'].find("ЦМО") != -1:
                self.cmo = 1
            index = tmp_index
            current_dict = cat['catalogResponse']['data']["category"][index]
            category_ids.append(current_dict["id"])
        with open("count.json", "r") as price_count_file:
            price_count_json = load(price_count_file)
            for count in price_count_json['main']:
                if(count['id'] == current_dict['id']):
                    return (category_ids, float(count["count"]))
        return (category_ids, 1)

    def product_take(self, PRICE_TYPE: int, json_data: dict, active_sheet: Any, id: str, mode: int) -> None:
        '''
        Main function. Create and modify xlsx price file.\n
        ``PRICE_TYPE`` - configuration number. Indicates what type of directory will be generated\n
        ``id`` - product id\n
        ``active_sheet`` - current openpyxl thread\n
        ``json_data`` - all goods from Netlab subcatalog\n
        Appending fields:\n
        #### PRICE_TYPE: 1
        * "Название категории 1 группы"
        * "Название категории 2 группы"
        * "Название категории 3 группы"\n
        #### PRICE_TYPE: 0 or 1
        * Артикул(XML_ID)
        * Название
        * Цена
        * Валюта
        '''
        data_len = len(json_data)
        active_sheet_row = active_sheet.max_row + 1
        self.cmo = 0
        p_info = self.find_count(id, self.diction)
        p_count, p_cat = p_info[1], p_info[0]
        p_cat.reverse()
        ind = 1
        catalog_dict = dict()
        catalog_dict = self.update_list(catalog_dict)
        for i in range(0, data_len):
            if json_data[i]['properties']["удаленный склад"] is not None and json_data[i]['properties']['цена по категории F'] != 0:
                if PRICE_TYPE == 1:
                    for index, ids in enumerate(p_cat, 1):
                        active_sheet.cell(row=active_sheet_row, column=index).value = self.find_name(
                            catalog_dict['catalogResponse']['data']['category'], ids)
                        ind = index
                    ind += 1
                active_sheet.cell(
                    row=active_sheet_row, column=ind).value = json_data[i]['properties']['id']
                ind += 1
                active_sheet.cell(
                    row=active_sheet_row, column=ind).value = json_data[i]['properties']['название']
                ind += 1
                if self.cmo != 1:
                    active_sheet.cell(row=active_sheet_row, column=ind).value = round(
                        json_data[i]['properties']['цена по категории F'] * self.usd_value * (1 + p_count), 2)
                else: # Condition of CMO company
                    active_sheet.cell(row=active_sheet_row, column=ind).value = round(
                        json_data[i]['properties']['РРЦ'], 2)
                ind += 1
                active_sheet.cell(row=active_sheet_row,
                                  column=ind).value = "RUB"
                active_sheet_row += 1
                ind = 1
                self.pandas_config(json_data[i], self.find_name(catalog_dict['catalogResponse']['data']['category'], p_cat[0])) if mode == 4 else None
            else:
                continue

    def init_main_xlsx(self, active_sheet: Any) -> None:
        '''
        Init columns names in xlsx start catalog file
        '''
        active_sheet["A1"].value = "Название категории 1 группы"
        active_sheet["B1"].value = "Название категории 2 группы"
        active_sheet["C1"].value = "Название категории 3 группы"
        active_sheet["D1"].value = "XML_ID"
        active_sheet["E1"].value = "Название"
        active_sheet["F1"].value = "Цена"
        active_sheet["G1"].value = "Val"

    def init_default_xlsx(self, active_sheet: Any) -> None:
        '''
        Init columns names in xlsx default file
        '''
        active_sheet["A1"].value = "XML_ID"
        active_sheet["B1"].value = "Название"
        active_sheet["C1"].value = "Цена"
        active_sheet["D1"].value = "Val"
