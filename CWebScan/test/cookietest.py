from requests import Request, Session

def testCookie():
    black_cookie_key_list = ['Domain', 'Path', 'session', 'Expires', 'JSESSIONID', 'PHPSESSID', 'Sess', 'csrf', 'secure', '__utma', '__utmz', 'UM_', 'CNZZ']
    cookie = "BAIDUID=50C1318B067EEBA42E350416ABBA0A80:FG=; BIDUPSID=50C1318B067EEBA42E350416ABBA0A80; PSTM=1553488351; BDUSS=FpKMTY1dmFDM3ZaQn5YQjBYVUE2THB3MTVYdzNiOHZibjdRb1ZNTERVVUwtTDljQVFBQUFBJCQAAAAAAAAAAAEAAAA2uXI4x6210QAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAtrmFwLa5hcO; __cfduid=d8593b58eeb2acffbc93fe2e24c90bba81554102539; BD_UPN=12314753; MSA_WH=768_472; H_WISE_SIDS=130611_125704_127760_131451_131379_131074_126062_130164_120137_131380_131601_118895_118862_131402_118853_118831_118791_130762_131651_131577_131536_131534_131530_130222_131295_131871_131391_129565_107320_131795_131393_130121_130569_131195_130347_117435_131242_129652_131023_127025_131435_131036_131045_130412_129901_129482_129644_124802_131424_130824_110085_127969_131506_123289_131753_131751_131749_131299_127318_130604_128195_131550_131827_131265_131262_128605_131458; plus_cv=1::m:49a3f4a6; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; BD_HOME=1; H_PS_PSSID=1424_28803_21081_28518_28767_28723_28964_28838_28585; delPer=0; BD_CK_SAM=1; PSINO=3; COOKIE_SESSION=12_0_7_4_3_6_0_1_5_4_1_0_63182_0_0_0_1557890506_0_1557894316%7C9%230_0_1557894316%7C1; H_PS_645EC=1103bSAp1couYWORn%2BDmemPFmZmJifVsqBfLzekf%2BUITpU8jSZHFIUPQV6Q; sugstore=1"
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
            cookieSplit = i.split('=')
            if len(cookieSplit) > 2:
                cookie_key = cookieSplit[0]
                cookie_value = '='.join(cookieSplit[1:])
            else:
                cookie_key = cookieSplit[0]
                cookie_value = cookieSplit[1]
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
    testCookie()