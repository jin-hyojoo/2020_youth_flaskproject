''' 전국 도서관 표준데이터 공공 API 활용

URL ▼
http://api.data.go.kr/openapi/tn_pubr_public_lbrry_api?type=json&serviceKey
=vl9GjXUBcZ4TryQq%2Focyh73456BFQ9i%2FlyEv97dBnw7TOEQbcu8YCmAtAhjKbVUDrTBDWr96qynv16%2FWXc5lPw%3D%3D
&ctprvnNm=%EC%84%9C%EC%9A%B8%ED%8A%B9%EB%B3%84%EC%8B%9C

필요데이터 ▼
lbrryNm(도서관명), lbrrySe(도서관유형), cctprvnNm(시도명),signguNm(시군구명),
closeDay(휴관), weekdayOperOpenHhmm(평일개방), weekdayOperColseHhmm(평일마감)
satOperOperOpenHhmm, satOperCloseHhmm (토요일 개방마감),
holidayOperOpenHhmm, holidayCloseOpenHhmm (공휴일 개방마감),
lonCo (대출가능권수),lonDaycnt (대출일자), rdnmadr(주소),
phoneNumber(번호), homepageUrl, latitude(위도), longitude(경도)

결과 | 데이터 예시 ▼
{"response":{"header":{"resultCode":"00","resultMsg":"NORMAL_SERVICE","type":"json"},"body":{"items":
[{"lbrryNm":"소나무언덕3호","ctprvnNm":"서울특별시","signguNm":"송파구","lbrrySe":"공공도서관","closeDay":"매주월요일+국가지정공휴일",
"weekdayOperOpenHhmm":"09:00","weekdayOperColseHhmm":"22:00","satOperOperOpenHhmm":"09:00","satOperCloseHhmm":"22:00",
"holidayOperOpenHhmm":"09:00","holidayCloseOpenHhmm":"22:00","seatCo":"84","bookCo":"24512","pblictnCo":"17",
"noneBookCo":"221","lonCo":"5","lonDaycnt":"14","rdnmadr":"서울특별시 송파구 성내천로 319 (마천동)",
"operInstitutionNm":"서울특별시 송파구청","phoneNumber":"02-443-0130","plotAr":"343","buldAr":"343",
"homepageUrl":"http://www.splib.or.kr","latitude":"37.492325","longitude":"127.156619","referenceDate":"2020-02-20",
"insttCode":"3230000",}..데이터 나열],"totalCount": "532","numOfRows": "10","pageNo": "1"}}}

'''

'''     ABOUT ERROR  - get_LibraryInfo() return부분
        - json.load시 오류발생
        - json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes: line 1 column 746 (char 745)
        - JSON 유효성 검사 진행 => http://jsonlint.com/
        - 원인: 각각의 아이템이 끝날 때 ",} 콤마가 붙으면 안되는데 붙어서 끝남
        - 해결: getUrl.py에서 데이터 갖고올 때 replace 진행
        
        MANAGED JSON DATE - get_LibraryPointData()
        - gungu컬럼 중 도봉구 지역만 '서울특별시 도봉구'와 같이 sido정보가 포함돼서 정제
        - 홈페이지 데이터 값 중 빈값이 아닌 '-' 값이 들어가 있어 ''으로 정제
        
'''

from getUrl import get_request_url
from config import *
import urllib.request
import pandas as pd
import json
import datetime
import math
import csv



# 공공데이터 중 '서울' 도서관 json으로 갖고오기
def get_KLibraryInfo(sido, nPageNum, nItems):
    endPoint = "http://api.data.go.kr/openapi/tn_pubr_public_lbrry_api"
    param = "?type=json&serviceKey=" + service_key
    param += "&ctprvnNm=" + urllib.parse.quote(sido)
    param += "&pageNo=" + str(nPageNum)
    param += "&numOfRows=" + str(nItems)
    url = endPoint + param
    DataResult = get_request_url(url)
    if (DataResult == None):
        return None
    else:
        return json.loads(DataResult)


# 공공데이터 데이터 존재 여부 확인
def chk_KLibraryData(KoreaLibData):
    try:
        # 정상적으로 데이터 들어왔는지 확인
        if (KoreaLibData['response']['header']['resultMsg'] == 'NORMAL_SERVICE'):
            nTotal = int(KoreaLibData['response']['body']['totalCount'])

            # 들어온 데이터 존재
            for item in KoreaLibData['response']['body']['items']:
                # json point data
                get_KLibraryClean(item, KjsonCleanData)
            # return save_csv(KjsonCleanData)
    except Exception as e:
        # 데이터 X에 대한 예외처리
        print(f'데이터 불러오기를 실패했습니다 : {e}')
        pass


# JSON NULL 데이터 관리작업 (데이터 정제)
def get_KLibraryClean(item, KjsonCleanData):
    libName = '' if 'lbrryNm' not in item.keys() else item['lbrryNm']
    lbiType = '' if 'lbrrySe' not in item.keys() else item['lbrrySe']
    sidoName = '' if 'ctprvnNm' not in item.keys() else item['ctprvnNm']
    gunguName = '도봉구' if '서울특별시 도봉구' in item.values() else item['signguNm']
    closeDay = '' if 'closeDay' not in item.keys() else item['closeDay']
    weekdayOpen = '' if 'weekdayOperOpenHhmm' not in item.keys() else item['weekdayOperOpenHhmm']
    weekdayClose = '' if 'weekdayOperColseHhmm' not in item.keys() else item['weekdayOperColseHhmm']
    satOpen = '' if 'satOperOperOpenHhmm' not in item.keys() else item['satOperOperOpenHhmm']
    satClose = '' if 'satOperCloseHhmm' not in item.keys() else item['satOperCloseHhmm']
    holidayOpen = '' if 'holidayOperOpenHhmm' not in item.keys() else item['holidayOperOpenHhmm']
    holidayClose = '' if 'holidayCloseOpenHhmm' not in item.keys() else item['holidayCloseOpenHhmm']
    # tk(take out)
    tkNum = 0 if 'lonCo' not in item.keys() else item['lonCo']
    tkDay = 0 if 'lonDaycnt' not in item.keys() else item['lonDaycnt']
    adrress = '' if 'rdnmadr' not in item.keys() else item['rdnmadr']
    phNum = '' if 'phoneNumber' not in item.keys() else item['phoneNumber']
    url = '' if '-' in item.values() else item['homepageUrl']
    # url = '' if 'homepageUrl' not in item.keys() else item['homepageUrl']
    latitude = 0 if 'latitude' not in item.keys() else item['latitude']
    longitude = 0 if 'longitude' not in item.keys() else item['longitude']
    KjsonCleanData.append({'libName': libName, 'lbiType': lbiType,
                           'sidoName': sidoName, 'gunguName': gunguName,
                           'closeDay': closeDay, 'weekdayTime': weekdayOpen + "-" + weekdayClose,
                           'satTime': satOpen + "-" + satClose, 'holidayTime': holidayOpen + "-" + holidayClose,
                           'tkNum': tkNum, 'tkDay': tkDay, 'adrress': adrress, 'phNum': phNum, 'url': url,
                           'latitude': latitude, 'longitude': longitude})


''' ▼ 서울열린데이터광장-필요데이터보충 '''


# 서울열린데이터광장 - 공공도서관 현황
def get_SLibraryInfo(startIndex, EndIndex):
    endPoint = "http://openapi.seoul.go.kr:8088/" + service_key_M + "/json/SeoulPublicLibraryInfo/"
    param = str(startIndex) + "/" + str(EndIndex)
    url = endPoint + param
    DataResult = get_request_url(url)
    if (DataResult == None):
        return None
    else:
        try:
            return json.loads(DataResult)
        except Exception as e:
            print("json load 오류 발생 :", e)


# 서울열린데이터광장 데이터 존재 여부 확인
def chk_SLibraryData(SeoulLibData):
    try:
        if (SeoulLibData['SeoulPublicLibraryInfo']['RESULT']['CODE'] == 'INFO-000'):
            nTotal = int(SeoulLibData['SeoulPublicLibraryInfo']['list_total_count'])
            for item in SeoulLibData['SeoulPublicLibraryInfo']['row']:
                # 필요한 서울특별시교육청~ 도서관 정보만
                if '서울특별시교육청' in item['LBRRY_NAME']:
                    get_SLibraryClean(item, SjsonCleanData)
    except Exception as e:
        print(f'데이터 불러오기를 실패했습니다 : {e}')
        pass


# 데이터 정제
def get_SLibraryClean(item, SjsonCleanData):
    # OP_TIME 데이터 정제
    s1 = item['OP_TIME']
    SliceTimeData = s1.split(' ')
    libName = '' if 'LBRRY_NAME' not in item.keys() else item['LBRRY_NAME']
    lbiType = '' if 'LBRRY_SE_NAME' not in item.keys() else item['LBRRY_SE_NAME']
    sidoName = '서울특별시' if '서울특별시' in item['ADRES'] else item['ADRES']
    gunguName = '' if 'CODE_VALUE' not in item.keys() else item['CODE_VALUE']
    closeDay = '' if 'FDRM_CLOSE_DATE' not in item.keys() else item['FDRM_CLOSE_DATE']
    weekdayTime = SliceTimeData[2].replace(',', '') if '평일' in s1 else item['OP_TIME']
    satTime = SliceTimeData[5] if '주말' in s1 else item['OP_TIME']
    holidayTime, tkNum, tkDay = '', '', ''
    adrress = '' if 'ADRES' not in item.keys() else item['ADRES']
    phNum = '' if 'TEL_NO' not in item.keys() else item['TEL_NO']
    url = '' if 'HMPG_URL' not in item.keys() else item['HMPG_URL']
    latitude = '' if 'XCNTS' not in item.keys() else item['XCNTS']
    longitude = '' if 'YDNTS' not in item.keys() else item['YDNTS']
    SjsonCleanData.append({'libName': libName, 'lbiType': lbiType,
                           'sidoName': sidoName, 'gunguName': gunguName,
                           'closeDay': closeDay, 'weekdayTime': weekdayTime,
                           'satTime': satTime, 'holidayTime': holidayTime,
                           'tkNum': tkNum, 'tkDay': tkDay, 'adrress': adrress,
                           'phNum': phNum, 'url': url, 'latitude': latitude, 'longitude': longitude})


''' csv 파일생성 '''


def save_csv(seoul):
    seoulLib = pd.DataFrame(seoul, columns=('libName', 'lbiType', 'sidoName', 'gunguName',
                                            'closeDay', 'weekdayTime', 'satTime',
                                            'holidayTime', 'tkNum', 'tkDay', 'adrress', 'phNum',
                                            'url', 'latitude', 'longitude'))
    seoulLib.to_csv('서울시_도서관표준데이터.csv', encoding='utf8', index=False)
    print('[%s] CSV save Success' % datetime.datetime.now())


''' json 파일생성 '''


def save_json():
    with open('static/서울시_도서관표준데이터.json', 'w', encoding='utf8') as outfile:
        s_library = json.dumps(KjsonCleanData + SjsonCleanData, indent=4, sort_keys=True, ensure_ascii=False)
        outfile.write(s_library)


# MAIN
if __name__ == '__main__':
    nPageNum, nItems = 1, 600  # 직접 값지정 말고 페이지 넘어가게 하는 반복문으로 생각해보기(?)
    startIndex, EndIndex = 1, 200  # 서울공공도서관용

    # managed json data 담을 리스트 변수
    KjsonCleanData = []
    SjsonCleanData = []

    # bring api data / check data
    KoreaLibData = get_KLibraryInfo('서울특별시', nPageNum, nItems)
    KJsonData = chk_KLibraryData(KoreaLibData)
    SeoulLibData = get_SLibraryInfo(startIndex, EndIndex)
    SJsonData = chk_SLibraryData(SeoulLibData)

    # save CSV / JSON
    # save_csv(KjsonCleanData+SjsonCleanData)
    save_json()
