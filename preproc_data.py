import pandas as pd
from datetime import datetime
import locale

locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')  # the ru locale is installed
df = pd.read_csv('entire-kamtoday.csv', index_col='id')

dates = []
for index, raw_timestamp in df['raw_timestamp'].iteritems():
    ex = raw_timestamp.split(',')[0]
    date = datetime.strptime(ex, '%d %B %Y')
    dates.append([date.year, date.month, date.day,
                 (date - datetime(2020, 1, 1)).days])

trans = list(zip(*dates))

df['year'] = trans[0]
df['month'] = trans[1]
df['day'] = trans[2]
df['ts_sort'] = trans[3]

df.to_csv('entire-kamtoday2.csv')