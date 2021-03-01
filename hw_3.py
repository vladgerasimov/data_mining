import requests, lxml, time, datetime
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
from database.db import DataBase


class GbBlogParser:
    def __init__(self, start_url, database:DataBase):
        self.db = database
        self.start_url = start_url
        self.tasks = []
        self.done_urls = set()

    def _get_response(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            return response
        time.sleep(0.5)

    def _get_soup(self, url):
        response = self._get_response(url)
        soup = bs(response.text, 'lxml')
        return soup

    def _create_task(self, url, callback, tag_list):
        for link in set(urljoin(url, href.attrs.get('href'))
                        for href in tag_list if href.attrs.get('href')):
            if link not in self.done_urls:
                task = self._get_task(link, callback)
                self.done_urls.add(link)
                self.tasks.append(task)

    def _parse_feed(self, url, soup):
        ul = soup.find('ul', attrs={'class': 'gb__pagination'})
        self._create_task(url, self._parse_feed, ul.find_all('a'))
        self._create_task(url, self._parse_posts, soup.find_all('a', attrs={'class': 'post-item__title'}))

    def _collect_children_comments(self, children):
        print(children)
        #for children in comment['comment']['children']:
        result = []
        data = {
            'user': children['comment']['user']['full_name'],
            'user_url': children['comment']['user']['url'],
            'text': children['comment']['body']
        }
        result.append(data)
        return result

    def _parse_comments(self, comments):
        result = []
        for comment in comments:
            data = {
                'id': comment['comment']['id'],
                'user': comment['comment']['user']['full_name'],
                'user_url': comment['comment']['user']['url'],
                'user_id': comment['comment']['user']['id'],
                'text': comment['comment']['body'],
                'parent_id': comment['comment']['parent_id']
            }
            result.append(data)
            result.extend(self._parse_comments(comment['comment']['children']))
        return result

    def _get_comments(self, url):
        try:
            comments = self._get_response(url).json()
            return self._parse_comments(comments)
        except AttributeError:
            return []


    def _parse_posts(self, url, soup):
        author_info = soup.find('div', attrs={'itemprop': 'author'})
        post_id = soup.find('div', attrs={'class': 'referrals-social-buttons-small-wrapper'})\
            .attrs.get('data-minifiable-id')
        comments_link = f'https://geekbrains.ru/api/v2/comments?commentable_type=Post&commentable_id={post_id}&order=desc'
        data = {
            'post_data': {
                'url': url,
                'title': soup.find('h1', attrs={'class': 'blogpost-title'}).text
            },
            'publication_date': self._get_date(soup),
            'first_image': soup.find('img').attrs.get('src'),
            'author': {
                'name': author_info.text,
                'url': urljoin(url, author_info.parent.attrs.get('href'))
            },
            'tags': [
                {'name': a_tag.text, 'url': urljoin(url, a_tag.attrs.get('href'))}
                     for a_tag in soup.find_all('a', attrs={'class': 'small'})
                     ],
            'comments': self._get_comments(comments_link)
        }
        return data

    def _get_date(self, soup):
        months = {'янв': 1,
                  'фев': 2,
                  'мар': 3,
                  'апр': 4,
                  'май': 5,
                  'мая': 5,
                  'июн': 6,
                  'июл': 7,
                  'авг': 8,
                  'сен': 9,
                  'окт': 10,
                  'ноя': 11,
                  'дек': 12}
        date_str = soup.find('time', attrs={'itemprop': 'datePublished'}).text
        date = date_str.split()
        result = datetime.datetime(year=int(date[2]), day=int(date[0]), month=months[date[1][:3]])
        return result

    def _get_task(self, url, callback):
        def task():
            soup = self._get_soup(url)
            return callback(url, soup)

        return task

    def run(self):
        self.tasks.append(self._get_task(self.start_url, self._parse_feed))
        self.done_urls.add(self.start_url)
        for task in self.tasks:
            result = task()
            if isinstance(result, dict):
                self.db.create_post(result)
                print(1)


if __name__ == '__main__':
    db = DataBase('sqlite:///hw_3.db')
    url = 'https://geekbrains.ru/posts'
    parser = GbBlogParser(url, db)
    parser.run()
