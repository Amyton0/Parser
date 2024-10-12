import requests
from playwright.sync_api import sync_playwright
import asyncio
from playwright.async_api import async_playwright


class Parser:
    def __init__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch()

    def parse(self, link):
        page = self.browser.new_page()
        page.goto(link)
        html = self.get_html(page)
        text = self.get_all_text(page)
        images = self.get_images(page)
        page.close()
        return {
            "html": html,
            "text": text,
            "images": images
        }

    def get_all_text(self, page):
        locator = page.locator(':has-text("")')
        text = '\n'.join(filter(lambda x: x and not x.isspace(), locator.all_inner_texts()))
        return text

    def get_html(self, page):
        return page.inner_html('*')

    def get_images(self, page):
        locators = page.get_by_role('img').all()
        return list(filter(lambda x: x, map(lambda x: x.get_attribute('src'), locators)))

    def kill(self):
        self.browser.close()
        self.playwright.stop()


parser = Parser()
print(parser.parse('https://habr.com/ru/companies/amvera/articles/835304/'))
parser.kill()
