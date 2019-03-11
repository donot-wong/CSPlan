#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-02-20 17:02:28
# @Author  : donot (donot@donot.me)
# @Link    : https://blog.donot.me

import pickle
import pika
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
from lib.rabbitqueue.consumerBase import ConsumerBase
from utils.globalParam import ScanLogger,  BlackParamName, ScanTaskStatus, VulnType, AlertTemplateDict
from utils.DataStructure import RequestData
from lib.scanscript.sqliscan.errorbased import plainArray, regexArray
from lib.models.datamodel import ScanTask, VulnData
from utils.commonFunc import send2slack


class SqliScanBase(object):
    """docstring for SqliScanBase"""
    SrcRequest = None
    def __init__(self, request, dbsession):
        self.SrcRequest = request
        self.dbsession = dbsession
        self.sendreqCnt = 0
        # ScanLogger.warning('__init__ called SqliScanBase')
    
    def run(self):
        '''
        线程中调用的函数
        '''
        # ScanLogger.warning('run called SqliScanBase')
        self.init()

        if self.method == 'GET':
            for key, value in self.getData.items():
                if key not in BlackParamName:
                    hasErrorSqliVuln = self.errorbased('params', key)
                    if hasErrorSqliVuln:
                        self.saveScanResult(VulnType['sqli-error'], key)
                        break
                    else:
                        hasTimeSqliVuln = self.timebased('params', key)
                        if hasTimeSqliVuln:
                            self.saveScanResult(VulnType['sqli-time'], key)
                            break
                        else:
                            continue
                else:
                    continue
        elif self.method == 'POST' and self.postData != '':
            for key, value in self.postData.items():
                if key not in BlackParamName:
                    hasErrorSqliVuln = self.errorbased('data', key)
                    if hasErrorSqliVuln:
                        self.saveScanResult(VulnType['sqli-error'], key)
                        break
                    else:
                        hasTimeSqliVuln = self.timebased('data', key)
                        if hasTimeSqliVuln:
                            self.saveScanResult(VulnType['sqli-time'], key)
                            break
                        else:
                            continue
                else:
                    continue
        else:
            pass

        self.changeScanStatus()

    def init(self):
        self.ct = self.SrcRequest.ct
        self.url = self.SrcRequest.scheme + '://' + self.SrcRequest.netloc + self.SrcRequest.path
        self.cookie = self.SrcRequest.cookie
        self.ua = self.SrcRequest.reqHeaders['User-Agent']
        self.getData = self.SrcRequest.getData
        self.postData = self.SrcRequest.postData
        self.method = self.SrcRequest.method
        self.SrcRequestHeaders = self.SrcRequest.reqHeaders
        self.saveid = self.SrcRequest.saveid
        self.scanid = self.SrcRequest.scanid
        # ScanLogger.warning('init function called')

    def errorbased(self, loc, key):
        if loc == 'params' and self.method == 'GET':
            _getData = copy.copy(self.getData)
            _getData[key] = _getData[key] + '\'"'
            res = self.reqSend(loc, _getData, self.url, self.method, self.cookie, self.ua, self.ct, self.SrcRequestHeaders)
            self.sendreqCnt += 1
            return self.checkIsErrorBaseSqli(res)
        elif loc == 'data' and self.method == 'POST':
            _postData = copy.copy(self.postData)
            _postData[key] = _postData[key] + '\'"'
            res = self.reqSend(loc, _postData, self.url, self.method, self.cookie, self.ua, self.ct, self.SrcRequestHeaders)
            self.sendreqCnt += 1
            return self.checkIsErrorBaseSqli(res)
        elif loc == 'params' and self.method == 'POST':
            return False
        else:
            ScanLogger.warning('Can not handle this request\'s method: %s' % self.method)
            return False

    def timebased(self, loc, key):
        '''
        基于时间延迟注入扫描
        '''

        if loc == 'params' and self.method == 'GET':
            _getData = copy.copy(self.getData)
            _getData
            return False
        elif loc == 'data' and self.method == 'POST':
            return False
        elif loc == 'params' and self.method == 'POST':
            return False
        else:
            ScanLogger.warning('Can not handle this request\'s method: %s' % self.method)
            return False

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
                timeout=10
            )
        except Exception as e:
            resp = None

        ScanLogger.warning('SqliScanBase reqSend function: send requests to: %s' % req.url)
        return resp

    def checkIsErrorBaseSqli(self, res):
        # dr = re.compile(r'<[^>]+>',re.S)
        # dd = dr.sub('', res.text)
        # print(res.text)
        # if int(res.headers['content-length']) < 4332:
        #     print(res.text)
        if res is None:
            return False
        else:
            dr = re.compile(r'<[^>]+>',re.S)
            dd = dr.sub('', res.text)
        for i in plainArray:
            if i in dd:
                ScanLogger.warning('SqliScanBase checkIsErrorBaseSqli function: find sqli base condition %s' % i)
                return True
        return False


    def checkIsTimeBaseSqli(self, res):
        pass

    def changeScanStatus(self, status = ScanTaskStatus['completed']):
        ScanLogger.warning('SqliScanBase scantask complete, scanid: %s' % self.scanid)
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
        # session.expunge_all()
        session.close()
        status, res = send2slack(AlertTemplateDict[str(vulntype)].format(vulnid=vulnid, scanid=self.scanid, url=self.url, method=self.method, paramname=paramname, detailUrl="http://webscan.donot.me?apikey=key&vulnid="+str(vulnid)))
        if status:
            ScanLogger.warning('Slack Alert Send Successfully! vulnid: %s' % vulnid)
        else:
            ScanLogger.error('Slack Alert Send Failed! Msg: %s, vulnid: %s' % (res, vulnid))



def startScan(data, dbsession):
    sqliscanObj = SqliScanBase(data, dbsession)
    sqliscanObj.run()


class SqliScanConsumer(ConsumerBase):
    def __init__(self, amqp_url, queue_name, routing_key, dbsession):
        super(SqliScanConsumer, self).__init__(amqp_url, queue_name, routing_key)
        self.scaning = 0
        self.scaned = 0
        self.pool =  ThreadPoolExecutor(max_workers=30)
        self.dbsession = dbsession


    def on_message(self, unused_channel, basic_deliver, properties, body):
        '''
        重写消息处理方法
        '''
        data = pickle.loads(body)
        ScanLogger.warning('SqliScanConsumer Received message # %s from %s: %s',
                    basic_deliver.delivery_tag, properties.app_id, data.netloc)
        self.acknowledge_message(basic_deliver.delivery_tag)
        sqliscanObj = SqliScanBase(data, self.dbsession)
        sqliscanObjfeaeture = self.pool.submit(sqliscanObj.run)
        self.scaning = self.scaning + 1
        ScanLogger.warning("SqliScanConsumer commit scantask, taskid: %s, now total scaning task: %s" % (data.scanid, self.scaning))
        sqliscanObjfeaeture.add_done_callback(self.threadcallback)
        while self.scaning > 35:
            ScanLogger.warning("SqliScanConsumer ThreadPool more than 30, now: {scaningnum}".format(scaningnum=self.scaning))
            time.sleep(3)

    def threadcallback(self, obj):
        print(obj.result())
        ScanLogger.warning("SqliScanConsumer task callback, now total scaning task: %s, scaned task: %s" % (self.scaning, self.scaned))
        self.scaning = self.scaning - 1
        self.scaned = self.scaned + 1



def SqliScanMain():
    engine = create_engine('mysql+pymysql://root:123456@127.0.0.1:3306/test',pool_size=20)
    DB_Session = sessionmaker(bind=engine)
    example = SqliScanConsumer('amqp://guest:guest@localhost:5672/%2F', 'sqliscan', 'sqliscan.key', DB_Session)
    try:
        example.run()
    except KeyboardInterrupt:
        example.stop()


def main():
    # http://43.247.91.228:81/vulnerabilities/sqli/?id=1&Submit=Submit#
    req = RequestData()
    req.saveid = 1
    req.scanid = 2
    req.ct = ''
    req.scheme = 'http'
    req.netloc = '43.247.91.228:81'
    req.method = 'GET'
    req.path = '/vulnerabilities/sqli/'
    req.cookie = 'PHPSESSID=vophvn0qp2am6m5h22l1tiev56; security=low'
    req.ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    req.getData = {'id': '1', 'Submit': 'Submit'}
    req.postData = ''
    req.reqHeaders = {'Cookie': 'PHPSESSID=vophvn0qp2am6m5h22l1tiev56; security=low', 'Accept-Language': 'zh-CN,zh;q=0.9', 'Accept-Encoding': 'gzip, deflate', 'Referer': 'http://43.247.91.228:81/vulnerabilities/sqli/', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8', 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36', 'Upgrade-Insecure-Requests': '1'}
    sqliscanObj = SqliScanBase(req, 'a')
    sqliscanObj.run()


if __name__ == '__main__':
    main()


