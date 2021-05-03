from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from bs4 import BeautifulSoup as bs
import requests as req
import pandas as pd
import time
import csv
import re

# from urllib.request import HTTPError
# from urllib.request import URLError
# from urllib.request import urlopen
# import collections
# from collections import OrderedDict


# 웹드라이버 설치
driver = webdriver.Chrome(ChromeDriverManager().install())

# 각 년도 browser를 얻기 위한 함수


def get_driver(year):
    driver.get("http://www.kyobobook.co.kr/bestSellerNew/bestseller.laf?range=1&kind=3&orderClick=DAC&mallGb=KOR&linkClass=A")
    elem = driver.find_element_by_class_name('btn_open')
    elem.click()
    time.sleep(2)
    elem = driver.find_element_by_link_text('50개씩 보기')
    elem.click()
    time.sleep(2)
    elem = driver.find_element_by_link_text('2020.01.01 ~ 2020.12.31')
    elem.click()
    time.sleep(2)
    elem = driver.find_element_by_link_text(f'{year}.01.01 ~ {year}.12.31')
    time.sleep(2)
    elem.click()
    time.sleep(2)


# 2020년 브라저 가져오기
get_driver(2020)

# 컬럼 값을 담을 리스트 생성
kyobo = []

# 크롤링 값을 얻기 위한 함수


def get_contents(soup):

    year_standard = soup.find(
        'h4', {'class': 'title_best_basic'}).find('small').text  # 집계기준 날짜

    bestseller_contents = soup.find('ul', {'class': 'list_type01'})

    bestseller_list = bestseller_contents.findAll(
        'div', {'class': 'detail'})  # 베스트 셀러 내용 리스트

    title_list = [b.find('div', {'class': 'title'}).find(
        'strong').text for b in bestseller_list]  # 제목

    rank = [b.find('strong').text.strip()
            for b in bestseller_list]  # 랭크

    author = [b.find('div', {'class': 'author'}).text.strip()[:9].strip()
              for b in bestseller_list]  # 작가

    review = [b.find('div', {'class': 'review'}).text.strip()[1:4]
              for b in bestseller_list]  # 리뷰개수

    subtitle_list = [b.find('div', {'class': 'subtitle'}).text.strip()
                     for b in bestseller_list]  # 부제

    book_price = [b.find('div', {'class': 'price'}).text.strip()[9:15]
                  for b in bestseller_list]  # 가격

    links = [b.find('a').attrs['href'] for b in bestseller_list]  # 상세페이지 링크

    tags = []  # 상세 페이지 내부 tag를 담을 리스트

    book_ratings = []  # 상세 페이지 내부 평점을 담을 리스트

    genre = []  # 장르를 담을 리스트

    publisher_list = []  # 출판사를 담을 리스트

    date_list = []  # 출판년도를 담을 리스트

    klover_review = []  # 클로버 리뷰를 담을 리스트

    # 접속 불가 상세페이지
    unused_url = ['http://www.kyobobook.co.kr/product/detailViewKor.laf?mallGb=KOR&ejkGb=KOR&barcode=9788925559650',
                  'http://www.kyobobook.co.kr/product/detailViewKor.laf?mallGb=KOR&ejkGb=KOR&barcode=9788965420354',
                  'http://www.kyobobook.co.kr/product/detailViewKor.laf?mallGb=KOR&ejkGb=KOR&barcode=9788965746614#review']

    # 상세페이지에 접속하면서 값을 얻어옴.
    for link in links:
        if link == unused_url[0] or link == unused_url[1]:
            tags.append('-')
            book_ratings.append(0)
            genre.append('')
            publisher_list.append('')
            date_list.append('')
            klover_review.append(0)
            continue
        # 태그 값을 얻기 위한 변경
        change_tag = '''(function($){
        $(document).ready(function() {
        var url = "http://api.eigene.io/rec/kyobo002";
        var params = ''' + link[-13:] + ''';
        var tagList = "";
        $.ajax({
            type: "get",
            url: url,
            data: {"format":"jsonp", "key": params},
            dataType : "jsonp",
            jsonp : "callback",
            success: function(data){
                if(data.groupedResults[params] != null){
                var keywordCnt = 6;
                if(data.groupedResults[params].length  < keywordCnt){
                    keywordCnt = data.groupedResults[params].length;
                }
                if(keywordCnt >= 1)
                    $(".box_detail_keywordpick").show();
                for(var i=0; i<keywordCnt ; i++)
                    tagList += data.groupedResults[params][i].itemId + " ";
                $(".book_keyword").html(tagList);
                }
            }
        });
    });
    }) (jQuery); '''

        # 링크 확인 및 BeautifulSoup으로 변경
        driver.get(link)
        driver.execute_script(change_tag)
        time.sleep(2)
        soup2 = bs(driver.page_source, 'html.parser')
        time.sleep(1)

        tags.append(soup2.find('div', class_='book_keyword').text)

        book_ratings.append(
            float(soup2.find('div', 'popup_load').find('em').string))

        publisher = soup2.find('span', {'title': '출판사'}).text.strip('\n')
        publisher_list.append(publisher)

        date = soup2.find("span", "date").text
        date = date.replace("\r", '')
        date = date.replace("\n", '')
        date = date.replace("\t", '')
        date_list.append(date)

        rows = soup2.find_all('p', class_='location')
        genre.append([row.get_text().strip() for row in rows])

        change_review = '''
        (function($){
        $('.list_share #cmt_share').hover(
            function(){$(this).find('#shareSocial').show();},
            function(){$(this).find('#shareSocial').hide();}
        ).find('a').focus(function(){
        $(this).addClass('focus');
        $(this).closest('#cmt_share').find('#shareSocial').stop().show();
        }).blur(function(){
        $(this).removeClass('focus');
        if (!$(this).closest('#cmt_share').find('.focus').size())
        $(this).closest('#cmt_share').find('#shareSocial').fadeOut(10);
        });
        $('.comment_wrap .image>a').click(function(e){
        e.preventDefault();
        $(this).parent().toggleClass('on');
        });
        })(jQuery);'''

        driver.get(link + '#review')
        driver.execute_script(change_review)
        time.sleep(1)
        # 링크 확인 및 BeautifulSoup으로 변경
        soup3 = bs(driver.page_source, 'html.parser')
        time.sleep(2)
        num = re.sub('[₩(₩)]', '', soup3.find(
            'span', class_='kloverTotal').text)
        time.sleep(1)
        klover_review.append(num)

    print("\n"+year_standard+"\n\n")

    # 각 정보를 kyobo 리스트에 담기 추후 csv로 변경
    for i in range(len(title_list)):
        kyobo.append({"Year": year_standard[8: 12], "Rank": rank[i], "Title": title_list[i], "Author": author[i],
                      "Review": review[i], 'Description': subtitle_list[i], "Price": book_price[i], "Tags": tags[i],
                      "Ratings": book_ratings[i], "Genre": genre[i], "Publisher": publisher_list[i], "Date": date_list[i], "Klover_review": klover_review[i]})


# 각 년도 별 페이지로 들어가 크롤링 수행
soup = bs(driver.page_source, 'html.parser')
time.sleep(3)
print('-------------------------------------')
print("1페이지입니다.", '\n')
get_contents(soup)

get_driver(2020)
elem = driver.find_element_by_link_text('2')
elem.click()
time.sleep(3)
print('-------------------------------------')
print("2페이지입니다.", "\n")
soup = bs(driver.page_source, 'html.parser')
time.sleep(3)

get_contents(soup)


time.sleep(2)
get_driver(2020)
elem = driver.find_element_by_link_text('3')
elem.click()
time.sleep(3)
print('-------------------------------------')
print("3페이지입니다.", "\n")
soup = bs(driver.page_source, 'html.parser')
time.sleep(3)
get_contents(soup)


time.sleep(2)
get_driver(2020)

elem = driver.find_element_by_link_text('4')
elem.click()
time.sleep(3)
print('-------------------------------------')
print("마지막 페이지입니다.", "\n")
soup = bs(driver.page_source, 'html.parser')
time.sleep(3)
get_contents(soup)

# 2019년
get_driver(2019)

elem = driver.find_element_by_css_selector(
    "#main_contents > div.list_header > div > span:nth-child(3) > a")
elem.click()
time.sleep(2)
elem = driver.find_element_by_link_text('2019.01.01 ~ 2019.12.31')
elem.click()
soup = bs(driver.page_source, 'html.parser')

time.sleep(2)
print('-------------------------------------')
print("1페이지입니다.", '\n')
get_contents(soup)

get_driver(2019)

elem = driver.find_element_by_link_text('2')
elem.click()
print('-------------------------------------')
print("2페이지입니다.", "\n")
time.sleep(2)

soup = bs(driver.page_source, 'html.parser')
get_contents(soup)


get_driver(2019)

time.sleep(2)
elem = driver.find_element_by_link_text('3')
elem.click()
print('-------------------------------------')
print("3페이지입니다.", "\n")
time.sleep(2)

soup = bs(driver.page_source, 'html.parser')
get_contents(soup)

get_driver(2019)

time.sleep(2)
elem = driver.find_element_by_link_text('4')
elem.click()
print('-------------------------------------')
print("마지막 페이지입니다.", "\n")
time.sleep(2)

soup = bs(driver.page_source, 'html.parser')
get_contents(soup)


# 2018년
get_driver(2018)
elem = driver.find_element_by_css_selector(
    "#main_contents > div.list_header > div > span:nth-child(3) > a")
elem.click()
time.sleep(2)
elem = driver.find_element_by_link_text('2018.01.01 ~ 2018.12.31')
elem.click()
soup = bs(driver.page_source, 'html.parser')

time.sleep(2)
print('-------------------------------------')
print("1페이지입니다.", '\n')
get_contents(soup)

get_driver(2018)
elem = driver.find_element_by_link_text('2')
elem.click()
print('-------------------------------------')
print("2페이지입니다.", "\n")
time.sleep(2)
soup = bs(driver.page_source, 'html.parser')
get_contents(soup)

get_driver(2018)
time.sleep(2)
elem = driver.find_element_by_link_text('3')
elem.click()
print('-------------------------------------')
print("3페이지입니다.", "\n")
time.sleep(2)
soup = bs(driver.page_source, 'html.parser')
get_contents(soup)

get_driver(2018)
time.sleep(2)
elem = driver.find_element_by_link_text('4')
elem.click()
print('-------------------------------------')
print("마지막 페이지입니다.", "\n")
time.sleep(2)
soup = bs(driver.page_source, 'html.parser')
get_contents(soup)

# 2017년
get_driver(2017)
elem = driver.find_element_by_css_selector(
    "#main_contents > div.list_header > div > span:nth-child(3) > a")
elem.click()
time.sleep(2)
elem = driver.find_element_by_link_text('2017.01.01 ~ 2017.12.31')
elem.click()
soup = bs(driver.page_source, 'html.parser')
time.sleep(2)
print('-------------------------------------')
print("1페이지입니다.", '\n')
get_contents(soup)

get_driver(2017)
elem = driver.find_element_by_link_text('2')
elem.click()
print('-------------------------------------')
print("2페이지입니다.", "\n")
time.sleep(2)
soup = bs(driver.page_source, 'html.parser')
get_contents(soup)

get_driver(2017)
time.sleep(2)
elem = driver.find_element_by_link_text('3')
elem.click()
print('-------------------------------------')
print("3페이지입니다.", "\n")
time.sleep(2)
soup = bs(driver.page_source, 'html.parser')
get_contents(soup)

get_driver(2017)

time.sleep(2)
elem = driver.find_element_by_link_text('4')
elem.click()
print('-------------------------------------')

print("마지막 페이지입니다.", "\n")
time.sleep(2)

soup = bs(driver.page_source, 'html.parser')
get_contents(soup)

# 2016년
get_driver(2016)

elem = driver.find_element_by_css_selector(
    "#main_contents > div.list_header > div > span:nth-child(3) > a")
elem.click()
time.sleep(2)
elem = driver.find_element_by_link_text('2016.01.01 ~ 2016.12.31')
elem.click()
soup = bs(driver.page_source, 'html.parser')

time.sleep(2)
print('-------------------------------------')
print("1페이지입니다.", '\n')
get_contents(soup)

get_driver(2016)

elem = driver.find_element_by_link_text('2')
elem.click()
print('-------------------------------------')
print("2페이지입니다.", "\n")
time.sleep(2)
soup = bs(driver.page_source, 'html.parser')
get_contents(soup)

get_driver(2016)

time.sleep(2)
elem = driver.find_element_by_link_text('3')
elem.click()
print('-------------------------------------')
print("3페이지입니다.", "\n")
time.sleep(2)
soup = bs(driver.page_source, 'html.parser')
get_contents(soup)

get_driver(2016)

time.sleep(2)
elem = driver.find_element_by_link_text('4')
elem.click()
print('-------------------------------------')
print("마지막 페이지입니다.", "\n")
time.sleep(2)
soup = bs(driver.page_source, 'html.parser')
get_contents(soup)

# 2015년
get_driver(2015)
elem = driver.find_element_by_css_selector(
    "#main_contents > div.list_header > div > span:nth-child(3) > a")
elem.click()
time.sleep(2)
elem = driver.find_element_by_link_text('2015.01.01 ~ 2015.12.31')
elem.click()
soup = bs(driver.page_source, 'html.parser')
time.sleep(2)
print('-------------------------------------')
print("1페이지입니다.", '\n')
get_contents(soup)

get_driver(2015)
elem = driver.find_element_by_link_text('2')
elem.click()
print('-------------------------------------')
print("2페이지입니다.", "\n")
time.sleep(2)
soup = bs(driver.page_source, 'html.parser')
get_contents(soup)

get_driver(2015)
time.sleep(2)
elem = driver.find_element_by_link_text('3')
elem.click()
print('-------------------------------------')
print("3페이지입니다.", "\n")
time.sleep(2)
soup = bs(driver.page_source, 'html.parser')
get_contents(soup)

get_driver(2015)
time.sleep(2)
elem = driver.find_element_by_link_text('4')
elem.click()
print('-------------------------------------')
print("마지막 페이지입니다.", "\n")
time.sleep(2)
soup = bs(driver.page_source, 'html.parser')
get_contents(soup)


# 데이터 사용을 위하여 csv로 컬럼 저장
with open('kyobo_bestseller.csv', 'w', newline='', encoding='utf-8') as f:
    field_names = ['Year', 'Rank', 'Title',
                   'Author', 'Review', 'Description', 'Price', 'Tags', 'Ratings', 'Genre', 'Publisher', 'Date', 'klover_review']
    writer = csv.DictWriter(f, fieldnames=field_names)
    writer.writeheader()
    for i in kyobo:
        writer.writerow({'Year': i['Year'], 'Rank': i['Rank'], 'Title': i['Title'], 'Author': i['Author'], 'Review': i['Review'],
                         'Description': i['Description'], 'Price': i['Price'], 'Tags': i['Tags'], 'Ratings': i['Ratings'], 'Genre': i['Genre'], 'Publisher': i['Publisher'], 'Date': i['Date'], 'klover_review': i['klover_review']})
