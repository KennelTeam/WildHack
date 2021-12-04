import pandas as pd


entire: pd.DataFrame = None
for i in range(10):
    path = f'scrapped/out{i}.csv'
    df = pd.read_csv(path, index_col='news_id')
    if i == 0:
        entire = df
    else:
        entire = entire.append(df)
entire.to_csv('entire.csv')