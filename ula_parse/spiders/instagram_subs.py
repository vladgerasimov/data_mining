import scrapy
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from ..items import InstagramUserItem
import time


class InstagramSubsSpider(scrapy.Spider):
    name = 'instagram_subs'
    allowed_domains = ['www.instagram.com']
    start_urls = ['http://www.instagram.com/']
    _login_url = 'https://www.instagram.com/accounts/login/ajax/'

    def __init__(self, login, password, users, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.login = login
        self.password = password
        self.users = users
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(5)

    def parse(self, response):
        self.browser.get(response.url)
        username_form = self.browser.find_element_by_name('username')
        username_form.send_keys(self.login)
        password_form = self.browser.find_element_by_name('password')
        password_form.send_keys(self.password)
        password_form.send_keys(Keys.ENTER)
        for _ in range(2):
            not_now_botton = self.browser.find_element_by_xpath('//button[contains(text(), "Не сейчас")]')
            not_now_botton.click()

        for user in self.users:
            yield response.follow(f'https://www.instagram.com/{user}/',
                                  callback=self._user_parse,
                                  cb_kwargs={'user': user})

    def _user_parse(self, response, **kwargs):
        user_name = kwargs['user']
        self.browser.get(response.url)
        item = InstagramUserItem()
        for idx in range(2):
            buttons = self.browser.find_elements_by_xpath('//a[contains(@class, "-nal3")]')
            buttons[idx].click()
            col = self.browser.find_element_by_xpath('//div[@class="isgrP"]')
            # time.sleep(1)
            len_users = len(self.browser.find_elements_by_xpath('//a[contains(@class, "FPmhX")]'))
            while True:
                for _ in range(50):
                    col.send_keys(Keys.PAGE_DOWN)
                time.sleep(4)
                users = self.browser.find_elements_by_xpath('//a[contains(@class, "FPmhX")]')
                if len_users == len(users):
                    break
                len_users = len(users)
            item['user'] = user_name
            item[self.browser.current_url.split('/')[-2]] = [
                {'name': user.text, 'url': f'https://www.instagram.com/{user.text}'}
                for user in users]
            close_button = self.browser.find_elements_by_xpath('//button[contains(@class, "wpO6b")]')
            close_button[1].click()
        yield item
