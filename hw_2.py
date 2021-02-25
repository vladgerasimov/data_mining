from bs4 import BeautifulSoup as bs
import lxml
from urllib.parse import urljoin
import requests
from pathlib import Path
import pymongo
import time
import datetime as dt


class ParserMagnit:
    def __init__(self, start_url, db_client):
        self.start_url = start_url
        self.db = db_client['data_mining']

    def _get_response(self, url):
        response = requests.get(url)
        while True:
            if response.status_code == 200:
                return response
            else:
                time.sleep(0.5)

    def _get_soup(self, url):
        response = self._get_response(url)
        return bs(response.text, 'lxml')

    def _date_str_to_datetime(self, product_a):
        date_str = product_a.find('div', attrs={'class': 'card-sale__date'}).text
        months = {'янв': 1,
                  'фев': 2,
                  'мар': 3,
                  'апр': 4,
                  'май': 5,
                  'июн': 6,
                  'июл': 7,
                  'авг': 8,
                  'сен': 9,
                  'окт': 10,
                  'ноя': 11,
                  'дек': 12}
        date_list = date_str.strip('\n').replace('с ', '').replace('до ', '').split('\n')
        result = []
        for date in date_list:
            date = date.split()
            if 'Только' in date:
                for _ in range(2):
                    result.append(
                        dt.datetime(
                            year=dt.datetime.now().year,
                            day=int(date[1]),
                            month=months[date[2][:3]]
                        ))
                return result
            result.append(
                dt.datetime(
                    year=dt.datetime.now().year,
                    day=int(date[0]),
                    month=months[date[1][:3]]
                )
            )
        if result[0].month > result[1].month:
            result[1] += dt.timedelta(days=365)
        return result

    def _get_prices(self, product_a):
        try:
            old_price = float(product_a.find('div', attrs={'class': 'label__price_old'})
                              .text.strip().replace('\n', '.'))
            new_price = float(product_a.find('div', attrs={'class': 'label__price_new'})
                              .text.strip().replace('\n', '.'))
            return old_price, new_price
        except ValueError:
            pass

    def _template(self):
        return {
            "url": lambda a: urljoin(self.start_url, a.attrs.get("href")),
            "promo_name": lambda a: a.find("div", attrs={"class": "card-sale__header"}).text,
            "title": lambda a: a.find("div", attrs={"class": "card-sale__title"}).text,
            'old_price': lambda a: self._get_prices(a)[0],
            'new_price': lambda a: self._get_prices(a)[1],
            "image_url": lambda a: urljoin(self.start_url, a.find('img').attrs.get('data-src')),
            "date_from": lambda a: self._date_str_to_datetime(a)[0],
            "date_to": lambda a: self._date_str_to_datetime(a)[1]
        }

    def _parse(self, product_a):
        product_data = {}
        for key, func in self._template().items():
            try:
                product_data[key] = func(product_a)
            except AttributeError:
                pass
        return product_data

    def _save(self, data):
        collection = self.db['magnit']
        collection.insert_one(data)

    def run(self):
        soup = self._get_soup(self.start_url)
        catalog = soup.find('div', attrs={'class': 'сatalogue__main'})
        for catalog_a in catalog.find_all('a', recursive=False):
            product_data = self._parse(catalog_a)
            self._save(product_data)


if __name__ == '__main__':
    url = 'https://magnit.ru/promo/?geo=moskva'
    db_client = pymongo.MongoClient()
    parser = ParserMagnit(url, db_client)
    parser.run()
