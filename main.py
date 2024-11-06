import asyncio
from playwright.async_api import async_playwright
import time
import math


async def parse(link, browser):
    page = await browser.new_page()

    try:
        await page.goto(link)
    except Exception as e:
        return None
    print(time.strftime('%X'))
    task_html = asyncio.create_task(get_html(page))
    task_text = asyncio.create_task(get_all_text(page))
    task_images = asyncio.create_task(get_images(page))

    html = await task_html
    text = await task_text
    images = await task_images
    await page.close()
    return {
        "html": html,
        "text": text,
        "images": images
    }


async def get_all_text(page):
    try:
        locator = page.locator(':has-text("")')
        text = '\n'.join(filter(lambda x: x and not x.isspace(), await locator.all_inner_texts()))
    except Exception as e:
        return None
    return text


async def get_html(page):
    try:
        html = await page.inner_html('*')
    except Exception as e:
        return None
    return html


async def get_images(page):
    try:
        locators = await page.get_by_role('img').all()
        images = list(filter(lambda x: x, await get_srcs(locators)))
    except Exception as e:
        return None
    return images


async def get_srcs(locators):
    return [await locator.get_attribute('src') for locator in locators]


async def main():
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch()

    sites = open('urls.txt', 'r')
    part_size = 100
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

    file = open('result.txt', 'w', encoding='UTF-8')
    file.write(str(result))

    await browser.close()
    await playwright.stop()


print(time.strftime('%X'))
asyncio.run(main())
print(time.strftime('%X'))
