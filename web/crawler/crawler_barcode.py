from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from bs4 import BeautifulSoup as bs
from urllib import parse
import requests as req
import pandas as pd
import time
import csv
import re

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
    elem = driver.find_element_by_link_text(f'{year}.01.01 ~ {year}.12.31')
    elem.click()
    time.sleep(2)


get_driver(2020)
# 값을 담을 리스트 생성
kyobo = []

soup = bs(driver.page_source, 'html.parser')


def get_contents(soup):

    year_standard = soup.find(
        'h4', {'class': 'title_best_basic'}).find('small').text  # 집계기준 날짜

    bestseller_contents = soup.find('ul', {'class': 'list_type01'})

    bestseller_list = bestseller_contents.findAll('div', {'class': 'detail'})

    title_list = [b.find('div', {'class': 'title'}).find(
        'strong').text for b in bestseller_list]  # 제목

    author = [b.find('div', {'class': 'author'}).text.strip()[:9].strip()
              for b in bestseller_list]

    links = [b.find('a').attrs['href'] for b in bestseller_list]

    barcodes = []

    for link in links:
        url = parse.urlparse(link)
        query = parse.parse_qs(url.query)
        query['barcode'][0]

        url = parse.urlparse(link)
        barcode = parse.parse_qs(url.query)['barcode'][0]
        barcodes.append(barcode)

    print("\n"+year_standard+"\n\n")
    for i in range(len(title_list)):
        kyobo.append({"Year": year_standard[8:12], "Rank": i+1, "Title": title_list[i], "Author": author[i],
                      "barcodes": barcodes[i]})


time.sleep(3)
print("1페이지입니다.", '\n')
get_contents(soup)
print('-------------------------------------')

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

soup = bs(driver.page_source, 'html.parser')
get_contents(soup)

# 2014년
get_driver(2014)

elem = driver.find_element_by_css_selector(
    "#main_contents > div.list_header > div > span:nth-child(3) > a")
elem.click()
time.sleep(2)
elem = driver.find_element_by_link_text('2014.01.01 ~ 2014.12.31')
elem.click()
soup = bs(driver.page_source, 'html.parser')

time.sleep(2)
print('-------------------------------------')
print("1페이지입니다.", '\n')
get_contents(soup)

get_driver(2014)

elem = driver.find_element_by_link_text('2')
elem.click()
print('-------------------------------------')
print("2페이지입니다.", "\n")
time.sleep(2)
soup = bs(driver.page_source, 'html.parser')
get_contents(soup)

get_driver(2014)

time.sleep(2)
elem = driver.find_element_by_link_text('3')
elem.click()
print('-------------------------------------')
print("3페이지입니다.", "\n")
time.sleep(2)
soup = bs(driver.page_source, 'html.parser')
get_contents(soup)

get_driver(2014)

time.sleep(2)
elem = driver.find_element_by_link_text('4')
elem.click()
print('-------------------------------------')

print("마지막 페이지입니다.", "\n")
time.sleep(2)

soup = bs(driver.page_source, 'html.parser')
get_contents(soup)

with open('kyobo_bestseller.csv', 'w', newline='', encoding='utf-8') as f:
    field_names = ['Year', 'Rank', 'Title',
                   'Author', 'barcodes']
    writer = csv.DictWriter(f, fieldnames=field_names)
    writer.writeheader()
    for i in kyobo:
        writer.writerow({'Year': i['Year'], 'Rank': i['Rank'], 'Title': i['Title'],
                         'Author': i['Author'], 'barcodes': i['barcodes']})
