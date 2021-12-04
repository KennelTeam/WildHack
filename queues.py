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

base_news_url = 'https://kamchatinfo.com/news/ecology/detail/{}/'
base_search_url = 'https://kamchatinfo.com/search/?q={}&how=d&from={}&to={}'

cur_progress = 0
max_progress = 48000
batch_count = 10
batch_step = max_progress // batch_count
# step = max_progress / 50


def increment_pbar():
    global cur_progress
    cur_progress += 1
    # if cur_progress % step == 0:
    printProgressBar(cur_progress, max_progress, 'scrap news')


def load_url(news_id, timeout):
    url = base_news_url.format(news_id)
    try:
        resp = requests.get(url, timeout=timeout)
        increment_pbar()
        try:
            if resp.status_code == 200:
                soup = bs4.BeautifulSoup(resp.text, 'html.parser')

                raw_date = soup.find('span', {'class': 'date'}).text
                timestamp = datetime.strptime(raw_date, '%d %B %Y %H:%M')

                title = soup.find('div', {'class': 'today'}).find('h1').text

                thumbnail_link = ''
                img_block = soup.find('div', {'class': 'photodet'})
                if img_block:
                    thumbnail_link = img_block.find('img')['src']

                content_found = soup.find(
                    'div', {'id': 'all_news'}).find_all('p')
                content_glued = ''
                for el in content_found:
                    content_glued += el.text + '\n'

                r_url = base_search_url.format(title, timestamp.strftime(
                    '%d.%m.%Y'), (timestamp + timedelta(1)).strftime('%d.%m.%Y'))
                search_resp = None
                while not search_resp:
                    search_resp = requests.get(r_url)
                soup_search = bs4.BeautifulSoup(
                    search_resp.text, 'html.parser')
                topic = soup_search.find(
                    'div', {'class': 'search-page'}).find_all('small')[-1].find_all('a')[-1].text

                # print(topic)
                if topic.strip() == 'Экология':
                    return [news_id, timestamp, title, thumbnail_link, content_glued]
        except Exception as e:
            if type(e) == requests.exceptions.ConnectionError:
                raise e
            print(f'bad parsing of {news_id}. E: {traceback.format_exc()}')
            return None
    except Exception as e:
        time.sleep(0.5)
        return load_url(news_id, timeout)



def do(p_start: int, p_finish: int):
    out = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONNECTIONS) as executor:
        future_to_url = (executor.submit(load_url, i, TIMEOUT)
                        for i in range(p_start, p_finish))
        time1 = time.time()
        for future in concurrent.futures.as_completed(future_to_url):
            resp = future.result()
            if resp:
                out.append(resp)

        time2 = time.time()
    print(f'Took {time2-time1:.2f} s')
    return out

locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')  # the ru locale is installed
for i in range(batch_count):
    out = do(batch_step*i, batch_step*(i+1))
    df = pd.DataFrame(columns=['news_id', 'timestamp', 'title', 'thumbnail_link', 'content'], data=out)
    df.set_index('news_id')
    df.to_csv(f'scrapped/out{i}.csv')