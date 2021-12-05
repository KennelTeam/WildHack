import pandas as pd
from datetime import datetime
import locale

locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')  # the ru locale is installed
df = pd.read_csv('entire-kamtoday2.csv', index_col='id')
df = df.drop(['timestamp_for_sort'], axis=1)

df.to_csv('entire-kamtoday2.csv')