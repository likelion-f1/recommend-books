from flask import Flask, render_template, request

# from wtforms import Form, TextAreaField, validators
# import pickle
# from flask_ngrok import run_with_ngrok
# import sqlite3
import os
import pandas as pd
import numpy as np
# from vectorizer import vect

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from ast import literal_eval
import warnings; warnings.filterwarnings('ignore')


app = Flask(__name__)
# run_with_ngrok(app)


### 데이터 처리 START ###
def weighted_score(record):
    v = record['Review']
    R = record['Ratings']
    n = record['newrank']
    b = record['bestcount']
    return (v / (v+m)) * R + (m / (v+m)) * C + (201 - n) / 20 + (b - 1) / 5

cur_dir = os.path.dirname(__file__)
# 코렙 실행의 경우 실행 위치를 명시
# cur_dir = os.getcwd() + '/'

# 교보문고 데이터
books_df = pd.read_csv(cur_dir + '/data/kyobo_best_final.csv')
books_df.info()
# print(books_df['Tags'].head())

# kaggle book-cross-data
books_cross_df = pd.read_csv(cur_dir + '/data/book_cross_data.csv')
books_cross_df.info()

books_rank_df = books_df[['Title', 'Year', 'Rank']]
bookcount = books_df['Title'].value_counts()
books_df['bestcount'] = bookcount.reindex(books_df.Title).tolist()
booked = books_df['Rank'].groupby(books_df['Title']).mean()
books_df['newrank'] = booked.reindex(books_df.Title).tolist()
books_df.drop_duplicates(['Title'], inplace=True)
books_df = books_df[['Year', 'Title', 'Author', 'Review', 'Description',
                     'Price', 'Tags', 'Genre', 'Ratings', 'bestcount',
                     'Rank', 'newrank',
                     'barcode', 'publisher', 'date']].reset_index(drop=True)

# 태그로추천
count_vect = CountVectorizer(min_df=0)
tags_mat = count_vect.fit_transform(books_df['Tags'])
tag_sim = cosine_similarity(tags_mat, tags_mat)
tag_sim_sorted_idx = tag_sim.argsort()[:, ::-1]

# 장르로 추천
books_df['Genre'] = books_df['Genre'].apply(literal_eval)
books_df['Genre'] = books_df['Genre'].apply(lambda x: (' ').join(x))
count_vect2 = CountVectorizer(min_df=0, ngram_range=(1, 2))
genres_mat = count_vect2.fit_transform(books_df['Genre'])
genre_sim = cosine_similarity(genres_mat, genres_mat)
genre_sim_sorted_idx = genre_sim.argsort()[:, ::-1]

# 가중치
C = books_df['Ratings'].mean()
m = books_df['Review'].quantile(0.6)

books_df['weighted2'] = books_df.apply(weighted_score, axis=1)


# 장르, 태그 둘다 사용
def find_sim_book(df, genre_sim, tag_sorted, title, topn=10):
    book = df[df['Title'] == title]
    idx = book.index.values
    sim_idx = tag_sorted[idx, :topn * 2].reshape(-1)
    sim_idx = sim_idx[sim_idx != idx]
    sim_idx = sim_idx[ genre_sim[idx[0]][sim_idx] > 0]
    return df.iloc[sim_idx].sort_values('weighted2', ascending=False)[:topn]


# book-cross 추천 함수
# 제목 검색 모델(book-cross)
def get_best_rating_userid_title(title, n):
    best_rating_user = books_cross_df[books_cross_df['book_title'] == title].sort_values('rating', ascending=False)['user_id'][:n].values
    return best_rating_user


def best_rating_user_book_title(user_id):
    recom_books=[]
    for id in user_id:
        df_combined = books_cross_df[books_cross_df['user_id'] == id].sort_values('rating', ascending=False)
        if len(recom_books) == 0:
            recom_books = df_combined
        else:
            recom_books = pd.concat([recom_books, df_combined])

    recom_books = recom_books.sort_values(by='rating', ascending=False).drop_duplicates(subset = 'book_title', keep = 'first')
    return recom_books.iloc[:10]


def recom_user_result_title(title):
    user_id = get_best_rating_userid_title(title, 5)
    books = best_rating_user_book_title(user_id)
    books = books[books != title]
    return books


# 작가 검색 모델(book-cross)
def get_best_rating_userid_author(author, n):
    best_rating_user = books_cross_df[books_cross_df['book_author'] == author].sort_values('rating', ascending=False)['user_id'][:n].values
    return best_rating_user


def best_rating_user_book_author(user_id):
    for id in user_id:
        df_combined = books_cross_df[books_cross_df['user_id'] == id].sort_values('rating', ascending=False)
        recom_books = pd.concat([df_combined, df_combined])
        recom_books = recom_books.sort_values(by='rating', ascending=False).drop_duplicates(subset = 'book_title', keep = 'first')
    return recom_books['book_title'][:10]


def recom_user_result_author(author):
  user_id = get_best_rating_userid_author(author, 5)
  books = best_rating_user_book_author(user_id)
  books = books[books != author]
  return books

### 데이터 처리 END ###

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')


@app.route('/search', methods=['GET', 'POST'])
def search():

    if request.method == 'GET':
        print('[search / GET] ', request.args)
        barcode = request.args.get('barcode')
        print(barcode)
        book = get_book_info_from_barcode(barcode)

    else:
        print('[search / POST] ', request.form)
        text = request.form['text']

        # 검색어 없을 때
        if text.strip() == '':
            return render_template('home.html')
        # 검색 책
        book = get_book_info(request.form)

    # 추천 책 목록
    books = get_recommended_books(book)
    return render_template('search.html', book=book, recommended_books=books)


def get_book_info_from_barcode(barcode):
    book = get_default_book()
    books = []
    try:
        books = books_df[books_df['barcode'] == int(barcode)]
    except Exception as e:
        print('wrong barcode for kyobo data:' + barcode)
    if len(books) > 0:
        book = books.iloc[0]
        book = get_book_obj(book)
    else:
        books = books_cross_df[books_cross_df['isbn'] == barcode]
        if len(books) > 0:
            book = books.iloc[0]
            book = get_book_obj2(book)
    return book


def get_default_book(kor=True):
    book = {"title": "검색 결과가 없습니다.",
                "author": ' ',
                "date": '',
                "rating": 0,
                "review": 0,
                "year": [],
                "rank": [],
                "publisher": " ",
                "image": "https://wnwn1223.nzine.co.kr/assets/m2/img/no_list.png",
                "price": " ",
                "keywords": [],
                "barcode": ' ',
                "success": False,
                'kor': kor
            }
    return book


def get_book_info(form):
    text = form['text']
    option = form['option']
    books = []

    if not text[0].encode().isalpha():
        # 교보문고 데이터에서 검색
        if option == 'title':
            books = books_df[books_df['Title'].apply(lambda x: text in x)]
        elif option == 'author':
            books = books_df[books_df['Author'].apply(lambda x: text in x)]

        print('[(KOR)search result]', books[['Title', 'Author']])

        # 검색 결과 없을 경우 (임시)
        if len(books) == 0:
            return get_default_book(kor=True)
        # 첫번째 검색 결과 return (임시)
        else:
            book = books.iloc[0]
            book = get_book_obj(book)
    else:
        # book-cross-data 에서 검색 (영어서적)
        text = text.lower()
        if option == 'title':
            books = books_cross_df[books_cross_df['book_title'].str.lower().apply(lambda x: text in x)]
        elif option == 'author':
            books = books_cross_df[books_cross_df['book_author'].str.lower().apply(lambda x: text in x)]

        print('[(ENG)search result]', books[['book_title', 'book_author']])

        # 검색 결과 없을 경우 (임시)
        if len(books) == 0:
            book = get_default_book(kor=False)
        # 첫번째 검색 결과 return (임시)
        else:
            book = books.iloc[0]
            book = get_book_obj2(book)

    return book


# csv 형식 book object 를 아래 형식으로 변환 (from 교보문고 csv)
def get_book_obj(csv_book):

    bar = str(int(csv_book.barcode))
    img_link = 'http://image.kyobobook.co.kr/images/book/large/' + bar[-3:] + '/l' + bar + '.jpg'

    try:
        book_ranks = books_rank_df[books_rank_df['Title'] == csv_book['Title']][['Year', 'Rank']]
        csv_book.Year = book_ranks.loc[:, 'Year']
        csv_book.Rank = book_ranks.loc[:, 'Rank']
    except Exception as e:
        print(e)

    book = {"title": csv_book.Title,
            "author": csv_book.Author,
            "date": csv_book.date,
            "rating": csv_book.Ratings,
            "review": csv_book.Review,
            "year": csv_book.Year,
            "rank": csv_book.Rank,
            "publisher": csv_book.publisher,
            "image": img_link,
            "price": csv_book.Price,
            "keywords": csv_book.Tags.split(' '),
            "barcode": bar,
            "success": True,
            'kor': True
            }
    return book


# csv 형식 book object 를 아래 형식으로 변환 (from book-cross-data csv)
def get_book_obj2(csv_book):
    book = {"title": csv_book.book_title,
            "author": csv_book.book_author,
            "date": csv_book.year_of_publication,
            "rating": csv_book.rating,
            "review": '',
            "year": [],
            "rank": [],
            "publisher": csv_book.publisher,
            "image": csv_book.img_m,
            "price": '',
            "keywords": [],
            "barcode": csv_book.isbn,
            "success": True,
            'kor': False
            }
    return book


def get_recommended_books(book):
    if not book['success']:
        return []

    if book['kor']:
        # 추천 시스템 실행
        books = find_sim_book(books_df, genre_sim, tag_sim_sorted_idx, book['title'])
        print('[recommended]', books[['Title', 'Author', 'Year']])
        books2 = []
        for i in books.index:
            books2.append(get_book_obj(books.loc[i]))
        return books2

    # book-cross 추천시스템 실행
    else:
        books = recom_user_result_title(book['title'])
        books3 = []
        for i in books.index:
          books3.append(get_book_obj2(books.loc[i]))
        return books3


if __name__ == '__main__':
    app.run()
    # print(books_df['Price'].head())