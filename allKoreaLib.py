
from getUrl import get_request_url
from config import *
import urllib.request
import pandas as pd
import json
import datetime
import math
import csv

''' ▼ 공공데이터 '''
# get json data on <libarary of 'seoul'> from the https://www.data.go.kr (API)
def get_KLibraryInfo(nPageNum,nItems):
    endPoint = "http://api.data.go.kr/openapi/tn_pubr_public_lbrry_api"
    param = "?type=json&serviceKey=" + service_key
    param += "&pageNo=" + str(nPageNum)
    param += "&numOfRows=" + str(nItems)
    url = endPoint+param
    DataResult = get_request_url(url)
    if(DataResult == None):
        return None
    else:
        return json.loads(DataResult)

# check the existence of data
def chk_KLibraryData(KoreaLibData):
    try:
        # check result data
        if (KoreaLibData['response']['header']['resultMsg'] == 'NORMAL_SERVICE'):
            nTotal = int(KoreaLibData['response']['body']['totalCount'])

            # existence result data
            for item in KoreaLibData['response']['body']['items']:
                # move to json point data
                get_KLibraryClean(item, KjsonCleanData)
        return KjsonCleanData
    except Exception as e:
        # exceptions for without data
        print(f'데이터 불러오기를 실패했습니다 : {e}')
        pass


# manage JSON data (clean up)
def get_KLibraryClean(item, KjsonCleanData):
    libName= '' if 'lbrryNm' not in item.keys() else item['lbrryNm']
    lbiType= '' if 'lbrrySe' not in item.keys() else item['lbrrySe']
    sidoName= '' if 'ctprvnNm' not in item.keys() else item['ctprvnNm']
    gunguName= '도봉구' if '서울특별시 도봉구' in item.values() else item['signguNm']
    closeDay= '' if 'closeDay' not in item.keys() else item['closeDay']
    weekdayOpen= '' if 'weekdayOperOpenHhmm' not in item.keys() else item['weekdayOperOpenHhmm']
    weekdayClose= '' if 'weekdayOperColseHhmm' not in item.keys() else item['weekdayOperColseHhmm']
    satOpen= '' if 'satOperOperOpenHhmm' not in item.keys() else item['satOperOperOpenHhmm']
    satClose= '' if 'satOperCloseHhmm' not in item.keys() else item['satOperCloseHhmm']
    holidayOpen= '' if 'holidayOperOpenHhmm' not in item.keys() else item['holidayOperOpenHhmm']
    holidayClose='' if 'holidayCloseOpenHhmm' not in item.keys() else item['holidayCloseOpenHhmm']
    # tk(take out)
    tkNum = 0 if 'lonCo' not in item.keys() else item['lonCo']
    tkDay = 0 if 'lonDaycnt' not in item.keys() else item['lonDaycnt']
    adrress = '' if 'rdnmadr' not in item.keys() else item['rdnmadr']
    phNum = '' if 'phoneNumber' not in item.keys() else item['phoneNumber']
    url =   '' if '-' in item.values() else item['homepageUrl']
    #url = '' if 'homepageUrl' not in item.keys() else item['homepageUrl']
    latitude = 0 if 'latitude' not in item.keys() else item['latitude']
    longitude = 0 if 'longitude' not in item.keys() else item['longitude']
    KjsonCleanData.append({'libName': libName, 'lbiType': lbiType,
                       'sidoName': sidoName, 'gunguName': gunguName,
                       'closeDay': closeDay, 'weekdayTime': weekdayOpen+"-"+weekdayClose,
                       'satTime': satOpen+"-"+satClose, 'holidayTime': holidayOpen+"-"+holidayClose,
                       'tkNum': tkNum, 'tkDay': tkDay,'address':adrress,'phNum': phNum, 'url': url,
                       'latitude':latitude, 'longitude': longitude})


''' ▼ 서울열린데이터광장:add the necessary information '''
# get json data on a <public libarary of 'seoul'> from the https://data.seoul.go.kr/ (API)
def get_SLibraryInfo(startIndex,EndIndex):
    endPoint = "http://openapi.seoul.go.kr:8088/" + service_key_M + "/json/SeoulPublicLibraryInfo/"
    param = str(startIndex) + "/" + str(EndIndex)
    url = endPoint + param
    DataResult = get_request_url(url)
    if(DataResult == None):
        return None
    else:
        try:
            return json.loads(DataResult)
        except Exception as e:
            print("json load 오류 발생 :", e)

# check the existence of data
def chk_SLibraryData(SeoulLibData):
    try:
        if (SeoulLibData['SeoulPublicLibraryInfo']['RESULT']['CODE'] == 'INFO-000'):
            nTotal = int(SeoulLibData['SeoulPublicLibraryInfo']['list_total_count'])
            for item in SeoulLibData['SeoulPublicLibraryInfo']['row']:
                # only Seoul Metropolitan Office of Education
                if '서울특별시교육청' in item['LBRRY_NAME']:
                    get_SLibraryClean(item, SjsonCleanData)
    except Exception as e:
        print(f'데이터 불러오기를 실패했습니다 : {e}')
        pass

# manage JSON data (clean up)
def get_SLibraryClean(item, SjsonCleanData):
    # OP_TIME data clean up
    s1 = item['OP_TIME']
    SliceTimeData = s1.split(' ')
    SliceLibData = item['LBRRY_NAME'].replace('서울특별시교육청','')

    libName = SliceLibData if '서울특별시' in item['LBRRY_NAME'] else item['LBRRY_NAME']
    lbiType = '' if 'LBRRY_SE_NAME' not in item.keys() else item['LBRRY_SE_NAME']
    sidoName = '서울특별시' if '서울특별시' in item['ADRES'] else item['ADRES']
    gunguName = '' if 'CODE_VALUE' not in item.keys() else item['CODE_VALUE']
    closeDay = '' if 'FDRM_CLOSE_DATE' not in item.keys() else item['FDRM_CLOSE_DATE']
    weekdayTime = SliceTimeData[2].replace(',','') if '평일' in s1 else item['OP_TIME']
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
                           'tkNum': tkNum, 'tkDay': tkDay, 'address': adrress,
                           'phNum': phNum, 'url': url, 'latitude': latitude, 'longitude': longitude})


# create csv file
def save_csv(seoul):
    seoulLib = pd.DataFrame(seoul, columns=('libName', 'lbiType', 'sidoName', 'gunguName',
                                                      'closeDay', 'weekdayTime', 'satTime',
                                                      'holidayTime', 'tkNum', 'tkDay', 'address', 'phNum',
                                                      'url', 'latitude', 'longitude'))
    seoulLib.to_csv('전국_도서관표준데이터.csv', encoding='utf8', index=False)
    print('[%s] CSV save Success' % datetime.datetime.now())

# create json file
def save_json():
    with open('static/전국_도서관표준데이터.json', 'w', encoding='utf8') as outfile:
        s_library = json.dumps(KjsonCleanData+SjsonCleanData, indent= 4, sort_keys=True, ensure_ascii=False)
        outfile.write(s_library)

# MAIN
if __name__ == '__main__':
    nPageNum, nItems = 1, 600  # 직접 값지정 말고 페이지 넘어가게 하는 반복문으로 생각해보기(?)
    startIndex, EndIndex = 1, 200 # for public library of seoul

    # use list variable to manage json data
    KjsonCleanData = []
    SjsonCleanData = []

    # bring api data / check data
    KoreaLibData = get_KLibraryInfo(nPageNum, nItems)
    KJsonData = chk_KLibraryData(KoreaLibData)
    SeoulLibData = get_SLibraryInfo(startIndex,EndIndex)
    SJsonData = chk_SLibraryData(SeoulLibData)

    # save CSV / JSON
    save_csv(KjsonCleanData+SjsonCleanData)
    save_json()
