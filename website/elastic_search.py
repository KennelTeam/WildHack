from elasticsearch import Elasticsearch, helpers
import csv
import pprint

es = Elasticsearch([{'host': '127.0.0.1', 'port': 9200}])

news_index = 'test12'


def load_data_from_csv():
    with open('../entire-kamtoday.csv') as f:
        reader = csv.DictReader(f)
        rows = []
        for index, row in enumerate(reader):
            row_temp = {
                'id': int(row['id']),
                'news_link': row['news_link'],
                'raw_timestamp': row['raw_timestamp'],
                'title': row['title'],
                'views_count': int(row['views_count']),
                'tags': row['tags'],
                'content': row['content'],
                'year': int(row['year']),
                'month': int(row['month']),
                'day': int(row['day']),
                'ts_sort': int(row['ts_sort'])
            }
            rows.append(row_temp)
        helpers.bulk(es, rows, index=news_index)


def make_keywords_query(keywords: list):
    return {
        "size": 10000,
        "query": {
            "bool": {
                "must": [{"match": {"tags": keyword}} for keyword in keywords]
            }
        }
    }


def search(query):
    res = es.search(
        index=news_index,
        body=query,
        filter_path=['hits.hits._source'],
        sort=['ts_sort']
    )
    return res if res == {} else res['hits']['hits']

# pprint.pprint(search(make_keywords_query(
#     ["#медведи"]
# )))
