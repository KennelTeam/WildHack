import flask
from flask import render_template, request, send_from_directory, redirect
from flask.scaffold import F
import pandas as pd
import os
from elastic_search import *
import json
import pprint

app = flask.Flask(__name__, static_folder='templates')
app.config['DEBUG'] = True
all_data = pd.read_csv('../entire-kamtoday.csv', index_col='id')
data: pd.DataFrame
inp_groups = json.loads(open("../groups.json", encoding='utf-8').read())


@app.route('/')
def default_page():
    return redirect('/cards')


@app.route('/cards')
def main_page():
    global data
    query_args = request.args
    order_by = query_args['order_by'] if 'order_by' in query_args else 'pub_date'
    order_desc = query_args['order_desc'] == '1' if 'order_desc' in query_args else '1'
    interests = [False, False, False]
    if 'low_interest' in query_args:
        interests[0] = True
    if 'medium_interest' in query_args:
        interests[1] = True
    if 'high_interest' in query_args:
        interests[2] = True
    if interests[0] == interests[1] == interests[2] == False:
        interests = [True, True, True]

    data = all_data

    if 'query' in query_args:
        query = query_args['query']
        keywords_list = ["#" + keyword for keyword in query.split()]
        data_ = search(make_keywords_query(keywords_list))
        if data_ != {}:
            data = data_
            data = list(map(lambda x: x['_source'], data))
            data = pd.DataFrame(data)

    years = []
    for year in data['year'].unique():
        cur_year: pd.DataFrame = data[data['year'] == year]

        if order_by == 'pub_date':
            cur_year = cur_year.sort_values(by=['ts_sort'])
        else:
            cur_year = cur_year.sort_values(by=['views_count'])
        pc = cur_year.shape[0]  # posts count
        toshow = pd.DataFrame(columns=cur_year.columns)
        if interests[0]:
            toshow = toshow.append(cur_year.iloc[:pc // 3])
        if interests[1]:
            toshow = toshow.append(cur_year.iloc[pc // 3:pc * 3 // 4])
        if interests[2]:
            toshow = toshow.append(cur_year.iloc[pc * 3 // 4:])

        if order_desc:
            toshow = toshow.iloc[::-1]

        toshow = toshow.drop_duplicates()
        cards = []
        for _, el in toshow.iterrows():
            mapped = {
                'id': el.name,
                'title': el['title'],
                'rating': el['views_count'],
                'date': el['raw_timestamp']
            }
            cards.append(mapped)
        years.append({
            'num': year,
            'cards': cards
        })
        years = years[::-1]

    return render_template('index.html', years=years)


@app.route('/post/<id>')
def show_post(id: int):
    id = int(id)
    cur_el = data.iloc[id]
    return render_template('post.html', title=cur_el['title'],
                           date=cur_el['raw_timestamp'],
                           rating=cur_el['views_count'],
                           content=cur_el['content'])


@app.route('/groups')
def groups():
    global data

    data = all_data

    res_groups = []
    for inp_group in inp_groups:
        cur_posts = []
        for post in inp_group['links']:
            df_post = data.loc[post['id']]
            post_res = {
                'id': post['id'],
                'title': df_post['title'],
                'date': df_post['raw_timestamp'],
                'rating': df_post['views_count']
            }
            cur_posts.append(post_res)
        res_groups.append({
            'id': inp_group['group_id'],
            'filename': inp_group['filename'],
            'news': cur_posts
        })

    res_groups = sorted(res_groups, key=lambda x: len(x['news']), reverse=True)

    return render_template('groups.html', groups=res_groups)


@app.route('/output_wordclouds/<path>')
def get_image(path):
    return send_from_directory(directory='../output_wordclouds', path=path)


@app.route('/group/<id>')
def get_group(id):
    id = int(id)
    group = next(filter(lambda group: group['group_id'] == id, inp_groups))
    cur_posts = []
    for post in group['links']:
        df_post = all_data.loc[post['id']]
        post_res = {
            'id': post['id'],
            'title': df_post['title'],
            'date': df_post['raw_timestamp'],
            'rating': df_post['views_count']
        }
        cur_posts.append(post_res)
    res = {
        'id': group['group_id'],
        'filename': group['filename'],
        'news': cur_posts
    }

    return render_template('single-group.html', group=res)


if __name__ == "__main__":
    app.run()
    # load_data_from_csv()