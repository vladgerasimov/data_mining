import scrapy, json, datetime
import requests, re
from urllib.parse import urljoin
from ..items import InstagramItem
from ..loaders import InstagramPostLoader, InstagramTagLoader

class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']
    _login_url = 'https://www.instagram.com/accounts/login/ajax/'
    _tag_url = '/explore/tags/'
    _pagination_url = 'https://www.instagram.com/graphql/query/?query_hash=9b498c08113f1e09617a1703c22b2f32&variables' \
                      '={"tag_name":"python","first":6,"after":' \
                      '"QVFCeWR3TVA3ejVPc21vSmpsa2tYTG9Sc3AxZktzbDFhMGhwOF9lVWVkNjBi' \
                      'THJUbmFidkxiQ1UyOWNJczEza2R1b042RkpBWXJqT1U2Mk1fZlViekxGQw=="}'

    def parse(self, response):
        try:
            js_data = self._get_json_data(response)
            yield scrapy.FormRequest(
                self._login_url,
                method='POST',
                callback=self.parse,
                formdata={'username': self.login,
                          'enc_password': self.password},
                headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:86.0) Gecko/20100101 Firefox/86.0',
                    'X-CSRFToken': js_data['config']['csrf_token']
                }
            )
        except AttributeError as e:
            print(e)
            if response.json()['authenticated']:
                for tag in self.tags:
                    yield response.follow(f'{self._tag_url}{tag}', callback=self._tag_page_parse)

    def _get_query_hash(self, response):
        url = 'https://www.instagram.com/'
        text = requests.get(urljoin(url, response.xpath("//link[contains(@href, 'TagPageContainer.js')]/@href")
                                    .extract_first())).text
        re_pattern = re.compile(r'queryId:"([a-zA-Z|\d]+)"')
        result = re.findall(re_pattern, text)
        return result[0]

    def _tag_page_parse(self, response):
        json_data = self._get_json_data(response)
        tag_item = self._get_tag_item(json_data)
        yield tag_item
        posts = json_data['entry_data']['TagPage'][0] \
            ['graphql']['hashtag']['edge_hashtag_to_media']['edges']
        for post in posts:
            post = self._get_post_item(post)
            yield post

        tag = json_data['entry_data']['TagPage'][0]['graphql']['hashtag']['name']
        end_cursor = json_data['entry_data']['TagPage'][0]['graphql']['hashtag']\
                              ['edge_hashtag_to_media']['page_info']['end_cursor']
        query_hash = self._get_query_hash(response)
        pagination_url = f'https://www.instagram.com/graphql/query/?query_hash={query_hash}&variables=' \
                         f'{{"tag_name":"{tag}","first":12,"after":"{end_cursor}"}}'
        yield response.follow(pagination_url, callback=self._parse_pagination, cb_kwargs={'query_hash': query_hash})

    def _parse_pagination(self, response, **kwargs):
        query_hash = kwargs['query_hash']
        json_data = json.loads(response.text)
        posts = json_data['data']['hashtag']['edge_hashtag_to_media']['edges']
        for post in posts:
            post = self._get_post_item(post)
            # loader = InstagramPostLoader()
            # loader.add_value('data', post['data'])
            # loader.add_value('date_parse', post['date_parse'])
            yield post

        has_next_page = json_data['data']['hashtag']['edge_hashtag_to_media']['page_info']['has_next_page']
        while has_next_page:
            tag = json_data['data']['hashtag']['name']
            end_cursor = json_data['data']['hashtag']['edge_hashtag_to_media']['page_info']['end_cursor']
            pagination_url = f'https://www.instagram.com/graphql/query/?query_hash={query_hash}&variables=' \
                             f'{{"tag_name":"{tag}","first":12,"after":"{end_cursor}"}}'
            yield response.follow(pagination_url, callback=self._parse_pagination, cb_kwargs={'query_hash': query_hash})

    @staticmethod
    def _get_tag_item(data):
        hashtag_data = data['entry_data']['TagPage'][0]['graphql']['hashtag']
        item = InstagramItem()
        item['_id'] = hashtag_data['id']
        item['date_parse'] = datetime.datetime.now()
        item['data'] = {
            'name': hashtag_data['name'],
            'profile_pic_url': hashtag_data['profile_pic_url']
        }
        return item

    @staticmethod
    def _get_post_item(post):
        post = post['node']
        item = InstagramItem()
        item['_id'] = post['id']
        item['date_parse'] = datetime.datetime.now()
        item['data'] = {
            'url': f'https://www.instagram.com/p/{post["shortcode"]}/',
            'media_url': [post['display_url']],
            'likes_count': post['edge_liked_by']['count'],
        }
        return item

    # def _parse_post(self, item):
    #     loader = InstagramPostLoader()
    #     loader.add_value('data', item['data'])
    #     loader.add_value('date_parse', item['date_parse'])
    #     yield loader.load_item()

    def __init__(self, login, password, tags, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.login = login
        self.password = password
        self.tags = tags

    @staticmethod
    def _get_json_data(response):
        script = response.xpath("//script[contains(text(), 'window._sharedData = ')]/text()").extract_first()
        return json.loads(script.replace('window._sharedData = ', '')[:-1])
