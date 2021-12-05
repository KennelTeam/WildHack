import flask
from flask import render_template, request, send_from_directory, redirect
from flask.scaffold import F
import pandas as pd
import os

app = flask.Flask(__name__, static_folder='templates')
app.config['DEBUG'] = True
all_data = pd.read_csv('../entire-kamtoday.csv', index_col='id')

@app.route('/')
def default_page():
    return redirect('/cards')

@app.route('/cards')
def main_page():
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
    years = []
    for year in all_data['year'].unique():
        cur_year: pd.DataFrame = all_data[all_data['year'] == year]
        if order_by == 'pub_date':
            cur_year = cur_year.sort_values(by=['ts_sort'])
        else:
            cur_year = cur_year.sort_values(by=['views_count'])
        pc = cur_year.shape[0] #posts count
        toshow = pd.DataFrame(columns=cur_year.columns)
        if interests[0]:
            toshow = toshow.append(cur_year.iloc[:pc//3])
        if interests[1]:
            toshow = toshow.append(cur_year.iloc[pc//3:pc*3//4])
        if interests[2]:
            toshow = toshow.append(cur_year.iloc[pc*3//4:])
        
        
        if order_desc:
            toshow = toshow.iloc[::-1]
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

    return render_template('index.html', years=years)


@app.route('/post/<id>')
def show_post(id: int):
    id = int(id)
    cur_el = all_data.iloc[id]
    return render_template('post.html', title=cur_el['title'],
                           date=cur_el['raw_timestamp'],
                           rating=cur_el['views_count'],
                           content=cur_el['content'])

@app.route('/groups')
def groups():
    return render_template('groups.html', groups=[
        {
            'img_link': '/imgs/1.jpg',
            'news': [
                {
                    'id': 1,
                    'title': 'azaza'
                },
                {
                    'id': 2,
                    'title': 'dudddudud'
                },
                {
                    'id': 3,
                    'title': 'looooooool'
                },
                {
                    'id': 11,
                    'title': 'lolkekcheburek'
                },
                {
                    'id': 345,
                    'title': 'elonmusk krutoy o da ochen silno krutoy'
                },
            ]
        },
        {
            'img_link': '/imgs/1.jpg',
            'news': [
                {
                    'id': 1,
                    'title': 'azaza'
                },
                {
                    'id': 2,
                    'title': 'dudddudud'
                },
                {
                    'id': 3,
                    'title': 'looooooool'
                },
                {
                    'id': 11,
                    'title': 'lolkekcheburek'
                },
                {
                    'id': 345,
                    'title': 'elonmusk krutoy o da ochen silno krutoy'
                },
            ]
        }
    ])

@app.route('/imgs/<path>')
def get_image(path):
   return send_from_directory(directory='imgs', path=path)

if __name__ == "__main__":
    app.run()