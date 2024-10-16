import requests
import urllib.request
from playwright.sync_api import sync_playwright
import asyncio
from playwright.async_api import async_playwright
import time
import playwright
import math


async def parse(link, browser):
    print("new page", link)
    page = await browser.new_page()

    try:
        print('loading', link)
        await page.goto(link)
    except Exception:
        print(link, 'parse')
        return None
    print(time.strftime('%X'))
    print(link, 'parsing started')
    task_html = asyncio.create_task(get_html(page))
    task_text = asyncio.create_task(get_all_text(page))
    task_images = asyncio.create_task(get_images(page))

    html = await task_html
    text = await task_text
    images = await task_images
    await page.close()
    print(link, 'parsing finished')
    return {
        "html": html,
        "text": text,
        "images": images
    }


async def get_all_text(page):
    # print('all text ' + page.url + ' started ' + time.strftime('%X'))
    try:
        locator = page.locator(':has-text("")')
        text = '\n'.join(filter(lambda x: x and not x.isspace(), await locator.all_inner_texts()))
    except Exception:
        print(page.url, 'text')
        return None
    # print('all text ' + page.url + ' finished ' + time.strftime('%X'))
    return text


async def get_html(page):
    # print('html ' + page.url + ' started ' + time.strftime('%X'))
    try:
        html = await page.inner_html('*')
    except Exception:
        print(page.url, 'html')
        return None
    # print('html ' + page.url + ' finished ' + time.strftime('%X'))
    return html


async def get_images(page):
    # print('images ' + page.url + ' started ' + time.strftime('%X'))
    try:
        locators = await page.get_by_role('img').all()
        images = list(filter(lambda x: x, await get_srcs(locators)))
    except Exception:
        print(page.url, 'img')
        return None
    # print('images ' + page.url + ' finished ' + time.strftime('%X'))
    return images


async def get_srcs(locators):
    return [await locator.get_attribute('src') for locator in locators]


async def main():
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch()

    sites = open('urls.txt', 'r')
    part_size = 300
    urls = sites.readlines()
    parts = math.ceil(len(urls) / part_size)
    urls_splitted = [urls[i * part_size:(i + 1) * part_size] for i in range(parts)]

    k = 0
    result = []
    for part in urls_splitted:
        tasks = []
        k += 1
        for url in part:
            tasks.append(asyncio.create_task(parse(url, browser)))

        n = 0
        for task in tasks:
            n += 1
            result.append(await task)
            print(k, n)

    file = open('result.txt', 'w')
    file.write(str(result))

    await browser.close()
    await playwright.stop()


print(time.strftime('%X'))
asyncio.run(main())
print(time.strftime('%X'))
