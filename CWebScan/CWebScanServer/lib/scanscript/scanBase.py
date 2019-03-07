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

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
from utils.globalParam import ScanLogger,  BlackParamName, ScanTaskStatus, VulnType, AlertTemplateDict
from utils.DataStructure import RequestData
from utils.commonFunc import send2slack


class ScanBase(object):
    SrcRequest = None
    def __init__(self, request, dbsession):
        self.SrcRequest = request
        self.dbsession = dbsession
        self.sendreqCnt = 0

    def init(self):
        self.ct = self.SrcRequest.ct
        self.urlRaw = self.SrcRequest.url
        self.url = self.SrcRequest.scheme + '://' + self.SrcRequest.netloc + self.SrcRequest.path
        self.cookie = self.SrcRequest.cookie
        self.ua = self.SrcRequest.reqHeaders['User-Agent']
        self.getData = self.SrcRequest.getData
        self.postData = self.SrcRequest.postData
        self.method = self.SrcRequest.method
        self.SrcRequestHeaders = self.SrcRequest.reqHeaders
        self.saveid = self.SrcRequest.saveid
        self.scanid = self.SrcRequest.scanid

    def run(self):
        self.init()
        self.repeatCheck()

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

    def repeatCheck(self, res_time, res_length):
        '''
        可重放检测
        没有Conetent-Length的包不做检测，依赖Cotent-Length进行检测，没有Content-Length暂时不做扫描
        '''
        respTimeList = []
        respLengthList = []
        for i in range(3):
            ela, headers = self.reqSendForRepeatCheck()
            if ela != 0 and headers is not None:
                respTimeList.append(ela.total_seconds())
                if 'Content-Length' in headers:
                    respLengthList.append(headers['Content-Length'])
                elif 'content-length' in headers:
                    respLengthList.append(headers['content-length'])
                else:
                    ctl = -1
            else:
                pass
        if len(respTimeList) == len(respLengthList) > 2:
            averageTime = sum(respTimeList) / len(respTimeList)
            averageLength = sum(respLengthList) / len(respLengthList)
        else:
            for i in range(2):
                pass



        # print(respTimeList)
        # print(respLengthList)


    def reqSendForRepeatCheck(self):
        s = Session()
        req = Request(self.method, 
            url = self.urlRaw,
            data = self.postData,
            headers = self.SrcRequestHeaders
        )
        prepped = s.prepare_request(req)
        try:
            resp = s.send(prepped, verify=False, timeout=20)
        except Exception as e:
            return 0, None
        return resp.elapsed, resp.headers


    def reqSend(self, loc, data, url, method, cookie, ua, ct, header):
        s = Session()
        if loc == 'params' and method == 'GET':
            req = Request(method, url,
                params = data,
                headers = header
            )
        elif loc == 'data' and method == 'POST':
            req = Request(method, url,
                data = data,
                headers = header
            )
        else:
            ScanLogger.warning('Can not handle this request\'s method: %s' % self.method)
            return None
        prepped = s.prepare_request(req)
        try:
            resp = s.send(prepped,
                verify=False,
                timeout=3
            )
        except Exception as e:
            resp = None

        ScanLogger.warning('ScanBase reqSend function: send requests to: %s' % req.url)
        return resp

def main():
    # http://43.247.91.228:81/vulnerabilities/sqli/?id=1&Submit=Submit#
    req = RequestData()
    req.saveid = 1
    req.scanid = 2
    req.ct = ''
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
    print(sum([1,2,3]))


