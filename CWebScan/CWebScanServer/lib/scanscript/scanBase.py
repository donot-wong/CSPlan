#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-03-07 11:48:33
# @Author  : donot (donot@donot.me)
# @Link    : https://blog.donot.me

import pickle
import sys
import os
import json
import re
from requests import Request, Session
import time
import copy
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
from utils.globalParam import ScanLogger,  BlackParamName, ScanTaskStatus, VulnType, AlertTemplateDict
from utils.DataStructure import RequestData
from lib.models.datamodel import ScanTask, VulnData
from utils.commonFunc import send2slack


class ScanBase(object):
    SrcRequest = None
    def __init__(self, request, dbsession):
        self.SrcRequest = request
        self.dbsession = dbsession
        self.sendreqCnt = 0

    def init(self):
        self.ct = self.SrcRequest.ct
        self.dataformat = self.SrcRequest.dataformat
        self.urlRaw = self.SrcRequest.url
        self.url = self.SrcRequest.scheme + '://' + self.SrcRequest.netloc + self.SrcRequest.path
        self.cookie = self.SrcRequest.cookie
        
        self.getData = self.SrcRequest.getData
        self.postData = self.SrcRequest.postData
        self.method = self.SrcRequest.method
        self.SrcRequestHeaders = self.SrcRequest.reqHeaders
        self.saveid = self.SrcRequest.saveid
        self.scanid = self.SrcRequest.scanid
        if 'Content-Length' in self.SrcRequestHeaders:
            self.ctl = self.SrcRequestHeaders['Content-Length']
        elif 'content-length' in self.SrcRequestHeaders:
            self.ctl = self.SrcRequestHeaders['content-length']
        else:
            self.ctl = 0
            self.NoLength = True

        if 'User-Agent' in self.SrcRequest.reqHeaders:
            self.ua = self.SrcRequest.reqHeaders['User-Agent']
        elif 'user-agent' in self.SrcRequest.reqHeaders:
            self.ua = self.SrcRequest.reqHeaders['user-agent']
        else:
            self.ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
        self.respTimeList = []
        self.cookie2Dict()

    def cookie2Dict(self):
        self.cookieDict = dict()
        self.cookieDict['other'] = []

        cookieList = self.cookie.split('; ')
        for i in cookieList:
            if '=' in i:
                cookieSplit = i.split('=')
                if len(cookieSplit) > 2:
                    cookie_key = cookieSplit[0]
                    cookie_value = '='.join(cookieSplit[1:])
                else:
                    cookie_key = cookieSplit[0]
                    cookie_value = cookieSplit[1]
                self.cookieDict[cookie_key] = cookie_value
            else:
                self.cookieDict['other'].append(i)

    def run(self):
        self.init()
        if not self.networkCheck():
            ScanLogger('ScanBase Network Check Failed, Please Check Network')
            return 0

        status, averageTime, averageLength = self.repeatCheck(self.ctl, self.NoLength)
        if status:
            pass
        else:
            ScanLogger(self.__class__.__name__ + ' repeatCheck Failed')
            self.changeScanStatus(ScanTaskStatus['repeat_check_failed'])

    def changeScanStatus(self, status = ScanTaskStatus['completed']):
        ScanLogger.warning(self.__class__.__name__ + ' scantask complete, scanid: %s' % self.scanid)
        session = self.dbsession()
        scans = session.query(ScanTask).filter_by(id=self.scanid).all()
        if len(scans) == 1:
            scans[0].status = status
            session.commit()
            session.close()

    def saveScanResult(self, vulntype, paramname):
        session = self.dbsession()
        vuln = VulnData(
            dataid = self.saveid,
            scanid = self.scanid,
            netloc = self.SrcRequest.netloc,
            vulntype = vulntype,
            paramname = paramname,
            status = 0
        )
        session.add(vuln)
        session.flush()
        vulnid = vuln.id
        session.commit()
        session.close()
        status, res = send2slack(AlertTemplateDict[str(vulntype)].format(vulnid=vulnid, scanid=self.scanid, url=self.url, method=self.method, paramname=paramname, detailUrl="http://webscan.donot.me?apikey=key&vulnid="+str(vulnid)))
        if status:
            ScanLogger.warning('Slack Alert Send Successfully! vulnid: %s' % vulnid)
        else:
            ScanLogger.error('Slack Alert Send Failed! Msg: %s, vulnid: %s' % (res, vulnid))

    def networkCheck(self):
        '''
        网络可用性检测
        '''
        try:
            s = Session()
            res = s.get('https://blog.donot.me/', timeout=5, allow_redirects=False)
            if res.status_code == 200:
                return True
            else:
                return False
        except Exception as e:
            return False


    def repeatCheck(self, res_length, NoLength=False):
        '''
        可重放检测
        没有Conetent-Length的包不做检测，依赖Cotent-Length进行检测，没有Content-Length暂时不做扫描
        '''
        if NoLength:
            return True, None, None
        respLengthList = []
        for i in range(3):
            ela, headers = self.reqSendForRepeatCheck()
            if headers is not None:
                self.respTimeList.append(ela)
                self.timesRcordList.append(ela)
                if 'Content-Length' in headers:
                    respLengthList.append(int(headers['Content-Length']))
                elif 'content-length' in headers:
                    respLengthList.append(int(headers['content-length']))
                else:
                    ctl = -1
            else:
                pass
        if len(respLengthList) > 1:
            averageLength = sum(respLengthList) / len(respLengthList)
        else:
            for i in range(3):
                ela, headers = self.reqSendForRepeatCheck()
                if headers is not None:
                    self.respTimeList.append(ela)
                    if 'Content-Length' in headers:
                        respLengthList.append(int(headers['Content-Length']))
                    elif 'content-length' in headers:
                        respLengthList.append(int(headers['content-length']))
                    else:
                        ctl = -1
                else:
                    pass

            if len(respLengthList) < 3:
                '''
                可重放性检测失败
                '''
                return False, None, None
            else:
                averageLength = sum(respLengthList) / len(respLengthList)

        ration = abs(averageLength - res_length) / res_length
        if ration < 0.2:
            return True, averageLength
        else:
            return False, averageLength


    def reqSendForRepeatCheck(self):
        s = Session()
        req = Request(self.method, 
            url = self.urlRaw,
            data = self.postData,
            headers = self.SrcRequestHeaders
        )
        prepped = s.prepare_request(req)
        try:
            resp = s.send(prepped, verify=False, timeout=20, allow_redirects=False)
        except Exception as e:
            return 0, None
        return resp.elapsed.total_seconds(), resp.headers


    def reqSend(self, loc, data=None, url=None, method=None, cookie=None, ua=None, ct=None, header=None):
        if data is None:
            getData = self.getData
            postData = self.postData
        if url is None:
            url = self.url
        if method is None:
            method = self.method
        if cookie is None:
            cookie = self.cookie
        if ua is None:
            ua = self.ua
        if ct is None:
            ct = self.ct
        if header is None:
            header = self.SrcRequestHeaders
        s = Session()
        if 'cookie' in header and 'Cookie' in header:
            header['cookie'] = header['Cookie']
            header.pop('Cookie')
        if 'referer' in header and 'Referer' in header:
            header['referer'] = header['Referer']
            header.pop('Referer')
        if 'user-agent' in header and 'User-Agent' in header:
            header['user-agent'] = header['User-Agent']
            header.pop('User-Agent')
        if loc == 'params' and method == 'GET':
            req = Request(
                method, 
                url,
                params = data,
                headers = header,
            )
        elif loc == 'data' and method == 'POST':
            req = Request(
                method, 
                url,
                params = self.getData,
                data = data,
                headers = header
            )
        elif loc == 'params' and method == 'POST':
            req = Request(
                method, 
                url, 
                params = data,
                data = self.postData,
                headers = header
            )
        elif loc == 'header':
            req = Request(
                self.method,
                self.url,
                params = getData,
                data = postData,
                headers = header
            )
        elif loc == 'empty':
            req = Request(
                method,
                url,
                params = getData,
                data = postData,
                headers = header
            )
        else:   
            ScanLogger.warning('Can not handle this request\'s method: %s' % self.method)
            return None
        prepped = s.prepare_request(req)
        try:
            resp = s.send(prepped,
                verify=False,
                timeout=15,
                allow_redirects=False
            )
        except Exception as e:
            resp = None

        ScanLogger.warning('ScanBase reqSend function: send requests to: %s' % req.url)
        return resp

    def dataTypeCheck(self, data):
        try:
            json.loads(data)
        except Exception as e:
            pass
        # return JSONLikeData
        # return XMLLikeData
    def cookieDict2Str(self, cookieDict):
        cookieStr = ''
        for key in cookieDict:
            if key == 'other':
                cookieStr = cookieStr + '; '.join(cookieDict['other'])
            else:
                cookieStr = cookieStr + '; ' + key + '=' + cookieDict[key]
        if cookieStr.startswith('; '):
            cookieStr = cookieStr[2:]
        return cookieStr


def main():
    # http://43.247.91.228:81/vulnerabilities/sqli/?id=1&Submit=Submit#
    req = RequestData()
    req.saveid = 1
    req.scanid = 2
    req.ct = ''
    # req.url = 'http://43.247.91.228:81/vulnerabilities/sqli/?id=1&Submit=Submit'
    req.url = 'http://43.247.91.228:81/vulnerabilities/sqli/?id=1&Submit=Submit'
    req.scheme = 'http'
    req.netloc = '43.247.91.228:81'
    req.method = 'GET'
    req.path = '/vulnerabilities/sqli/'
    req.cookie = 'PHPSESSID=vophvn0qp2am6m5h22l1tiev56; security=low'
    req.ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    req.getData = {'id': '1', 'Submit': 'Submit'}
    req.postData = ''
    req.reqHeaders = {'Cookie': 'PHPSESSID=vophvn0qp2am6m5h22l1tiev56; security=low', 'Accept-Language': 'zh-CN,zh;q=0.9', 'Accept-Encoding': 'gzip, deflate', 'Referer': 'http://43.247.91.228:81/vulnerabilities/sqli/', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8', 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36', 'Upgrade-Insecure-Requests': '1'}
    sqliscanObj = ScanBase(req, 'a')
    sqliscanObj.run()


if __name__ == '__main__':
    # print(sum([1,2,3]))
    main()
