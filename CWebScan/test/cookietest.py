from requests import Request, Session

def testCookie():
    black_cookie_key_list = ['Domain', 'Path', 'session', 'Expires', 'JSESSIONID', 'PHPSESSID', 'Sess', 'csrf', 'secure', '__utma', '__utmz', 'UM_', 'CNZZ']
    cookie = "_twitter_sess=BAh7CSIKZmxhc2hJQzonQWN0aW9uQ29udHJvbGxlcjo6Rmxhc2g6OkZsYXNo%250ASGFzaHsABjoKQHVzZWR7ADoPY3JlYXRlZF9hdGwrCJlG4a5qAToHaWQiJWUz%250AZTY0ZjRlYTgxN2U2N2Y1ZTZlYmZhOTc0ZjRjYmNjOgxjc3JmX2lkIiViNTk4%250AODkxYTE3N2EyZGU1NmI4Njg3OTRmNjFjNDkwNg%253D%253D--1b66942f7812237d1b7a41dfda972886ccaa5f0e; Path=/; Domain=.twitter.com; Secure; HTTPOnly"
    cookieList = cookie.split('; ')
    # for i in range(len(cookieList)):
    #   if '=' in cookieList[i]:
    #       for black_cookie_key in black_cookie_key_list:
    #           flag = False
    #           if black_cookie_key.lower() in cookieList[i].split('=')[0].lower():
    #               flag = True
    #               break
    #       if flag:
    #           continue
    #       else:
    #           cookieList[i] = cookieList[i] + '\''
    #           print('; '.join(cookieList))
    cookieDict = dict()
    cookieDict['other'] = []
    for i in cookieList:
        if '=' in i:
            cookie_key, cookie_value = i.split('=')
            cookieDict[cookie_key] = cookie_value
        else:
            cookieDict['other'].append(i)
    print(cookieDict)
    print(cookieDict2Str(cookieDict))

def cookieDict2Str(cookieDict):
    cookieStr = ''
    for key in cookieDict:
        if key == 'other':
            cookieStr = cookieStr + '; '.join(cookieDict['other'])
        else:
            cookieStr = cookieStr + '; ' + key + '=' + cookieDict[key]
    return cookieStr


def testcookie2():
    s = Session()
    url = 'http://120.24.224.32:22334'
    method = 'GET'
    header = {
        'User-Agent': "test-ua",
        'Referer': 'refer',
        'Cookie': 'Domain=Baidu.com'
    }
    cookie = {
        'Domain': 'baidu.com'
    }

    data = {
        'id': '1'
    }

    req = Request(
        method, 
        url,
        data = data,
        headers = header,
        cookies = cookie
    )
    prepped = s.prepare_request(req)
    resp = s.send(prepped,
        verify=False,
        timeout=15,
        allow_redirects=False
    )
    
    print(req.__dict__)



if __name__ == '__main__':
    # testCookie()
    testcookie2()