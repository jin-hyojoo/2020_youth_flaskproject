import datetime
import urllib.request

def get_request_url(url):
    req = urllib.request.Request(url)

    try:
        response = urllib.request.urlopen(url)
        if response.getcode() == 200:
            # print('[%s] Url Request Success' %datetime.datetime.now())

            # json Sysntax Error modify
            mdf = response.read().decode('utf-8')
            return mdf.replace(",}","}")
    except Exception as e:
        print(e)
        # print("[%s] Error for URL : %s" %(datetime.datetime.now(), url))
        return None
