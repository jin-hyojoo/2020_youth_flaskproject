import json
from math import ceil
from getUrl import get_request_url
from urllib import parse, request
from bs4 import BeautifulSoup
import xml

lib_code = {'MA': '강남도서관', 'MB': '강동도서관', 'MC': '강서도서관', 'MD': '개포도서관', 'ME': '고덕평생학습관', 'MF': '고척도서관', 'MG': '구로도서관',
            'MH': '남산도서관', 'MV': '노원평생학습관', 'MJ': '도봉도서관', 'MK': '동대문도서관', 'ML': '동작도서관', 'MX': '마포평생아현분관',
            'MM': '마포평생학습관', 'MP': '서대문도서관', 'MW': '송파도서관', 'MN': '양천도서관', 'MQ': '어린이도서관', 'MR': '영등포평생학습관',
            'MS': '용산도서관', 'MT': '정독도서관', 'MU': '종로도서관'}

# define how to sort
SORT_WAY = 'SORT_TITLE ASC'  # SORT_PUBLISHER, PUB_YEAR_INFO

'''
def searchbook(title):
    # because library code is necessary, this loop makes all library visited
    for libcode in lib_code.keys():

        endpoint = 'http://openapi-lib.sen.go.kr/openapi/service/lib/openApi?'
        query = [('serviceKey', service_key_B), ('title', title), ('manageCd', libcode), ('pageNo', '2'),
                 ('numOfRows', '5')]
        # query = f'serviceKey={service_key_B}&title={parse.quote(title)}&manageCd={libcode}'
        url = endpoint + parse.urlencode(query, doseq=True)
        # url = endpoint+query
        print(url)
        # send request by url and receive response
        response = get_request_url(url)
        # confirm if response is right
        if response is None:
            return None
        else:
            # parse response data (xml)
            xml = BeautifulSoup(response, features='lxml')
            # if result code doesn't exist or is not 00, there is something wrong
            if xml.find('resultCode') or xml.find('resultCode') != '00':
                return None  # "Response Error"
            else:
                return parsexml(xml)


def parsexml(xml):
    book_list = []
    # find books
    for book in xml.find_all('item'):
        book_list.append({
            'title': book.find('title').get_text(),
            'isbn': book.find('isbn').get_text(),
            'libname': book.find('libName').get_text(),
            'publisher': book.find('publisher').get_text(),
            'author': book.find('author').get_text()
        })
    return book_list
'''


# remove useless html tag
def tag_check(msg):
    if '<b>' in msg:
        msg = msg.replace('<b>', '')
    if '</b>' in msg:
        msg = msg.replace('</b>', '')
    return msg


# must enter the book value to find rec_key
def book_check(title, author, page, per_page):
    endpoint = 'https://nl.go.kr/kolisnet/openApi/open.php?'
    query = [('page', page),
             ('search_field1', 'title'),
             ('value1', title),
             ('and_or_not1', 'AND'),
             ('search_field2', 'author'),
             ('value2', author),
             ('per_page', per_page),
             ('sort_ksj', SORT_WAY)]
    url = endpoint + parse.urlencode(query, doseq=True)
    print(f'[DEBUG] URL : {url}')
    data_result = get_request_url(url)

    if data_result is None:
        return None
    else:
        xml = BeautifulSoup(data_result, features='lxml')
        if xml.find('error_info'):
            return None
        else:
            return xml


def book_name(title, author):
    lib_rec_key = {}
    page, per_page = 1, 100
    x = book_check(title, author, page, 1)
    if x is None:
        return None
    total = int(x.find('total').get_text())
    cnt = ceil(total / per_page)
    for idx in range(1, cnt + 1):
        xml = book_check(title, author, idx, per_page)
        for recode in xml.find_all('record'):
            lib_rec_key[recode.find('rec_key').get_text()] = {
                'title': tag_check(recode.findChild('title').get_text()),
                'author': tag_check(recode.findChild('author').get_text()),
                'publisher': recode.findChild('publisher').get_text(),
                'pubyear': recode.findChild('pubyear').get_text()}
    return lib_rec_key


# find library information using rec_key
def book_lib(book_list):
    result = {}
    endpoint = 'https://nl.go.kr/kolisnet/openApi/open.php?'
    # loop for all kinds of book including the title
    for item in book_list.keys():
        param = 'rec_key=' + item
        url = endpoint + param
        bookList = get_request_url(url)
        if bookList is None:
            return None
        else:
            # parse response data (xml)
            xml = BeautifulSoup(bookList, features='lxml')
            for loc in xml.find_all('lib_name'):
                # rec_key is a key to find library having the book
                if item in result:
                    result[item].append(loc.get_text())
                else:
                    result[item] = [loc.get_text()]
    return result


if __name__ == "__main__":
    # USAGE-------------------------------
    # title is necessary, author is optional
    # booklist = book_name(title, author)
    # librarylist = book_lib(booklist)

    bl = book_name('신데렐라', '초록개구리')
    print(f'[DEBUG] Book library count : {len(bl)}\n'
          f'[DEBUG] Book list {json.dumps(bl, ensure_ascii=False, indent=4)}')
    print(json.dumps(book_lib(bl), ensure_ascii=False, indent=4))

