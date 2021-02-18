import requests
from pathlib import Path
import time
import json


class Parser5:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/88.0.4324.182 Safari/537.36'
    }

    def __init__(self, categories_url, categories_path):
        self.categories_path = categories_path
        self.categories_url = categories_url
        self.categories = {}

    def _get_response(self, url):
        while True:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response
            time.sleep(0.5)

    def _parse_categories(self, url):
        response = self._get_response(url)
        data = response.json()
        for item in data:
            self.categories[int(item["parent_group_code"])] = item["parent_group_name"]

    def _parse_products(self):
        for code in self.categories:
            url = f'https://5ka.ru/api/v2/special_offers/?store=&records_per_page=12&page=1&categories={code}' \
                  f'&ordering=&price_promo__gte=&price_promo__lte=&search='
            result = {'name': self.categories[code], 'code': code, 'products': []}
            while url:
                response = self._get_response(url)
                data = response.json()
                url = data['next']
                result['products'].append(data['results'])
                yield result

    @staticmethod
    def _save(category, categories_path):
        json_category = json.dumps(category, ensure_ascii=False)
        categories_path.write_text(json_category, encoding='UTF-8')

    def run(self):
        self._parse_categories(self.categories_url)
        for category in self._parse_products():
            category_path = self.categories_path.joinpath(f"{category['name']}.json")
            self._save(category, category_path)


if __name__ == '__main__':
    categories_url = 'https://5ka.ru/api/v2/categories/'
    categories_path = Path(__file__).parent.joinpath('categories_with_products')
    if not categories_path.exists():
        categories_path.mkdir()

    parser = Parser5(categories_url, categories_path)
    parser.run()