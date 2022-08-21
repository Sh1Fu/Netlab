from json import load
from typing import Any
from requests import get
import xml.etree.ElementTree as ET


class UpdatePrice:
    def __init__(self, file_name) -> None:
        self.file_name = file_name
        self.usd_value = self.usd()

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
            index = tmp_index
            current_dict = cat['catalogResponse']['data']["category"][index]
            category_ids.append(current_dict["id"])
        with open("count.json", "r") as price_count_file:
            price_count_json = load(price_count_file)
            for count in price_count_json['main']:
                if(count['id'] == current_dict['id']):
                    return (category_ids, float(count["count"]))
        return (category_ids, 1)

    def product_take(self, PRICE_TYPE: int, json_data: dict, active_sheet: Any, id: str) -> None:
        '''
        Main function. Create and modify xlsx price file.\n
        ``PRICE_TYPE`` - configuration number. Indicates what type of directory will be generated
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
        p_info = self.find_count(id, self.diction)
        p_count, p_cat = p_info[1], p_info[0]
        p_cat.reverse()
        ind = 1
        catalog_dict = dict()
        catalog_dict = self.update_list(catalog_dict)
        for i in range(0, data_len):
            if json_data[i]['properties']["удаленный склад"] is not None:
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
                active_sheet.cell(row=active_sheet_row, column=ind).value = round(
                    json_data[i]['properties']['цена по категории F'] * self.usd_value * (1 + p_count), 2)
                ind += 1
                active_sheet.cell(row=active_sheet_row,
                                  column=ind).value = "RUB"
                active_sheet_row += 1
                ind = 1
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
