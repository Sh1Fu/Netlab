from urllib.error import HTTPError, URLError
from requests import get
from urllib.request import urlretrieve
from openpyxl import load_workbook
from json import loads
from tqdm import tqdm
from shutil import make_archive, move
from os import listdir, makedirs
from os.path import exists
from time import sleep
# http://services.netlab.ru/rest/catalogsZip/goodsImages/<goodsId>.xml?oauth_token=<token>


class DownloadImage:
    def __init__(self, token: str, file_name: str) -> None:
        self.token = token
        self.file_name = file_name

    def xlsx_work(self) -> None:
        '''
        Main active function. Edit xlsx file. Add image's name to "E" column. Download first product's image
        '''
        if not exists("images/"):
            makedirs("images/")
        self.wb = load_workbook(filename=self.file_name, read_only=False)
        self.active_s = self.wb.active
        length = self.active_s.max_row
        current_column = self.active_s.max_column + 1
        self.active_s.cell(row=1, column=current_column).value = "Картинка"
        for i in tqdm(range(2, length + 1, 1)):
            product_info = self.take_image(self.active_s["A%d" % i].value)
            if product_info != "":
                self.active_s.cell(row=i, column=current_column).value = str(i) + ".jpg"
                try:
                    urlretrieve(product_info, filename="images/%d.jpg" % i)
                    sleep(0.2)
                except BaseException or URLError or HTTPError:
                    sleep(120)
                    continue
        self.wb.save("images.xlsx")

    def take_image(self, id: str) -> str:
        '''
        API function. Take json with image's urls from Netlab API.
        Return value: image url or blank string
        '''
        response = get("http://services.netlab.ru/rest/catalogsZip/goodsImages/%s.json?oauth_token=%s" % (id, self.token))
        data = loads(response.text[response.text.find("& {") + 2:])
        if data['entityListResponse']['data'] != None:
            return data['entityListResponse']['data']['items'][0]['properties']['Url']
        return ""

    def sort_files(self, delit: int, files: list) -> None:
        '''
        Split all images to different dirs. Make zip archives after that
        '''
        a = files
        for i in range(1, (len(files) // delit) + 1):
            dir_name = f'images/images-{i}'
            if not exists(dir_name):
                makedirs(dir_name)
            for j in range(delit):
                move(f"images/images/{a[j]}", f"{dir_name}")
                print(f"move {a[j]} into {dir_name}")
            make_archive(f"images-{i}.zip", 'zip', f'images/images-{i}/')
            a = a[delit:]

    def images_zip(self) -> None:
        '''
        Create zip with images to NetLab
        '''
        a = listdir("../Netlab/images")
        count_of_files = len(a)
        mxDel = 0
        for i in range(1, count_of_files):
            if count_of_files % i == 0 and i >= mxDel:
                mxDel = i
        print(mxDel, len(a))
        self.sort_files(mxDel, a)

        make_archive("images.zip", 'zip', 'images/')
