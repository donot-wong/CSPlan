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
from utils.globalParam import ScanLogger,  BlackParamName, ScanTaskStatus, VulnType
from utils.DataStructure import RequestData
from lib.scanscript.sqliscan.errorbased import plainArray, regexArray
from lib.models.datamodel import ScanTask, VulnData


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
        self.errorbased()

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
        ScanLogger.warning('init function called')

    def errorbased(self):
        # ScanLogger.warning('errorbased called SqliScanBase')
        if self.method == 'GET':
            # ScanLogger.warning('errorbased function: start GET method test!')
            for key, value in self.getData.items():
                _getData = copy.copy(self.getData)
                _getData[key] = value + '\''
                res = self.reqSend(_getData, self.url, self.method, self.cookie, self.ua, self.ct, self.SrcRequestHeaders)
                self.sendreqCnt = self.sendreqCnt + 1
                hasSqliVuln = self.checkIsErrorBaseSqli(res)
                if hasSqliVuln:
                    self.saveScanResult(VulnType['sqli-error'])
                    self.changeScanStatus()
                    # return
                    ScanLogger.warning('SqliScanBase find errorbased sqli! scanid: %s, saveid: %s' % (self.scanid, self.saveid))
                    return 0
        elif self.method == 'POST':
            _postData = self.postData
        else:
            ScanLogger.warning('Can not handle this request\'s method: %s' % self.method)
        self.changeScanStatus()



    def reqSend(self, data, url, method, cookie, ua, ct, header):
        s = Session()
        req = Request(method, url,
            params = data,
            headers = header
        )
        prepped = s.prepare_request(req)
        resp = s.send(prepped,
            verify=False,
            timeout=3
        )
        ScanLogger.warning('SqliScanBase reqSend function: send requests to: %s' % req.url)
        return resp

    def checkIsErrorBaseSqli(self, res):
        # dr = re.compile(r'<[^>]+>',re.S)
        # dd = dr.sub('', res.text)
        for i in plainArray:
            if i in res.text:
                ScanLogger.warning('SqliScanBase checkIsErrorBaseSqli function: find sqli base condition %s' % i)
                return True


    def checkIsTimeBaseSqli(self, res):
        pass

    def changeScanStatus(self, status = ScanTaskStatus['completed']):
        session = self.dbsession()
        scans = session.query(ScanTask).filter_by(id=self.scanid).all()
        if len(scans) == 1:
            scans[0].status = status
            session.commit()


    def saveScanResult(self, vulntype):
        vuln = VulnData(
            dataid = self.saveid,
            scanid = self.scanid,
            vulntype = vulntype,
            status = 0
        )
        session = self.dbsession()
        session.add(vuln)
        session.commit()



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
        
        sqliscanObjfeaeture = self.pool.submit(startScan, data, self.dbsession)
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
    engine = create_engine('mysql+pymysql://root:123456@127.0.0.1:3306/test')
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


