import concurrent.futures
from functools import reduce
import requests
import time
import pandas as pd
import bs4
from datetime import datetime, timedelta
import locale
import traceback

from utils import printProgressBar

CONNECTIONS = 40
TIMEOUT = 5

base_site_url = 'https://kamtoday.ru{}'
base_search_url = 'https://kamtoday.ru/search/?tags=&period=0&q=&how=d&from=01.12.2010&to=05.12.2021&section=7&author=&PAGEN_1={}'
# base_search_url = 'https://kamchatinfo.com/search/?q={}&how=d&from={}&to={}'

cur_progress = 0
pages_count = 44
max_progress = 43*30
batch_count = 11
batch_step = pages_count // batch_count
# step = max_progress / 50


def increment_pbar():
    global cur_progress
    cur_progress += 1
    printProgressBar(cur_progress, max_progress, 'scrap news', length=90)


def load_page(page_id, timeout):
    url = base_search_url.format(page_id)
    try:
        resp = requests.get(url, timeout=timeout)
        page_soup = bs4.BeautifulSoup(resp.text, 'html.parser')
        news_blocks = page_soup.find_all('div', {'class': 'news-item'})
        links = list(map(lambda x: x.find('a')['href'], news_blocks))
        pages_resp = []
        for news_link in links:
            news_url = base_site_url.format(news_link)
            news_soup = bs4.BeautifulSoup(
                requests.get(news_url).text, 'html.parser')

            title = news_soup.find(
                'div', {'class': 'news-detail'}).find('div', {'class': 'name'}).text
            raw_timestamp = news_soup.find(
                'div', {'class': 'news-date-time'}).text

            tags_block = news_soup.find('div', {'class': 'news-tags'})
            tags = []
            if tags_block:
                tags_links = tags_block.find_all('a')
                tags = list(map(lambda x: x.text, tags_links))

            content_paragraphs = news_soup.find(
                'div', {'class': 'news-detail'}).find_all('p')
            content = ''.join(map(lambda x: x.text, content_paragraphs))

            gspans = news_soup.find('div', {'class': 'news-topinfo'}).find_all(
                'span')
            views_count = int(gspans[1].text.strip())

            increment_pbar()
            pages_resp.append([news_link, raw_timestamp, title, views_count, tags, content])
        return pages_resp

    except Exception as e:
        time.sleep(0.5)
        print(f'Error: {traceback.format_exc()}')
        return load_page(page_id, timeout)


def do(p_start: int, p_finish: int):
    out = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONNECTIONS) as executor:
        future_to_url = (executor.submit(load_page, i, TIMEOUT)
                         for i in range(p_start, p_finish))
        time1 = time.time()
        for future in concurrent.futures.as_completed(future_to_url):
            resp = future.result()
            if resp:
                out += resp

        time2 = time.time()
    print(f'Took {time2-time1:.2f} s')
    return out


locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')  # the ru locale is installed
increment_pbar()
for i in range(batch_count):
    out = do(batch_step*i, batch_step*(i+1))
    df = pd.DataFrame(columns=['news_link', 'raw_timestamp', 'title', 'views_count', 'tags', 'content'], data=out)
    df.to_csv(f'scrap-kamtoday/out{i}.csv')
