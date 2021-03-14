from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose
from urllib.parse import urljoin
from .items import InstagramItem


def get_salary(salary_list):
    minimum = None
    maximum = None
    for idx, item in enumerate(salary_list):
        if item == 'от ':
            minimum = salary_list[idx + 1]
        elif item == ' до ':
            maximum = salary_list[idx + 1]
    if maximum and minimum:
        return f'{minimum} - {maximum}'
    elif not maximum and not minimum:
        return 'Salary is unknown'
    elif not maximum:
        return f'from {minimum}'
    elif not minimum:
        return f'up to {maximum}'


def get_text(data):
    return "".join(data)


def get_employer_url(user_id):
    return urljoin('https://hh.ru/', user_id[0])


class AutoUlaLoader(ItemLoader):
    default_item_class = dict
    title_out = TakeFirst()
    price_out = TakeFirst()
    description_out = TakeFirst()
    seller_out = TakeFirst()


class HhVacancyLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
    title_out = TakeFirst()
    salary_out = get_salary
    description_out = get_text
    employer_url_out = get_employer_url


class HhEmployerLoader(ItemLoader):
    default_item_class = dict
    company_url_out = TakeFirst()
    company_name_out = TakeFirst()
    description_out = get_text


class InstagramPostLoader(ItemLoader):
    default_item_class = InstagramItem


class InstagramTagLoader(ItemLoader):
    default_item_class = InstagramItem
