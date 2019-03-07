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
import requests
import time
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
from lib.rabbitqueue.consumerBase import ConsumerBase
from utils.globalParam import ScanLogger, BlackParamName
from utils.DataStructure import RequestData
from lib.scanscript.scanBase import ScanBase

class RceScan(ScanBase):
    """docstring for RceScan"""
    def __init__(self, request, dbsession):
        super(RceScan, self).__init__(request, dbsession)

    def run(self):
        self.init()

        if self.method == 'GET':
            for key, value in self.getData.items():
                if key not in BlackParamName:
                    hasErrorSqliVuln = self.responsebased('params', key)
                    if hasErrorSqliVuln:
                        self.saveScanResult(VulnType['rce'], key)
                        break
                    else:
                        hasTimeSqliVuln = self.dnslogbased('params', key)
                        if hasTimeSqliVuln:
                            self.saveScanResult(VulnType['rce']. key)
                            break
                        else:
                            continue
                else:
                    continue
        elif self.method == 'POST' and self.postData != '':
            for key, value in self.postData.items():
                if key not in BlackParamName:
                    hasErrorSqliVuln = self.responsebased('data', key)
                    if hasErrorSqliVuln:
                        self.saveScanResult(VulnType['rce'], key)
                        break
                    else:
                        hasTimeSqliVuln = self.dnslogbased('data', key)
                        if hasTimeSqliVuln:
                            self.saveScanResult(VulnType['rce'], key)
                            break
                        else:
                            continue
                else:
                    continue
        else:
            pass

        self.changeScanStatus()

    def responsebased(self, loc, key):
        return False

    def dnslogbased(self, loc, key):
        return False

    def weblogbased(self, loc, key):
        return False


class RceScanConsumer(ConsumerBase):
    def __init__(self, amqp_url, queue_name, routing_key, dbsession):
        super(RceScanConsumer, self).__init__(amqp_url, queue_name, routing_key)
        self.scaning = 0
        self.scaned = 0
        self.pool =  ThreadPoolExecutor(30)
        self.dbsession = dbsession

    def on_message(self, unused_channel, basic_deliver, properties, body):
        '''
        重写消息处理方法
        '''
        data = pickle.loads(body)
        ScanLogger.warning('RceScanConsumer Received message # %s from %s: %s',
                    basic_deliver.delivery_tag, properties.app_id, data.netloc)
        self.acknowledge_message(basic_deliver.delivery_tag)
        rcescanObj = RceScan(data, self.dbsession)
        rcescanObjfeaeture = self.pool.submit(rcescanObj.run)
        self.scaning = self.scaning + 1
        ScanLogger.warning("RceScanConsumer commit scantask, taskid: %s, now total scaning task: %s" % (data.scanid, self.scaning))
        rcescanObjfeaeture.add_done_callback(self.threadcallback)
        while self.scaning > 35:
            ScanLogger.warning("RceScanConsumer ThreadPool more than 30, now: {scaningnum}".format(scaningnum=self.scaning))
            time.sleep(3)

    def threadcallback(self, obj):
        print(obj.result())
        ScanLogger.warning("RceScanConsumer task callback, now total scaning task: %s, scaned task: %s" % (self.scaning, self.scaned))
        self.scaning = self.scaning - 1
        self.scaned = self.scaned + 1



def RceScanMain():
    engine = create_engine('mysql+pymysql://root:123456@127.0.0.1:3306/test',pool_size=20)
    DB_Session = sessionmaker(bind=engine)
    rce = RceScanConsumer('amqp://guest:guest@localhost:5672/%2F', 'rcescan', 'rcescan.key', DB_Session)
    try:
        rce.run()
    except KeyboardInterrupt:
        rce.stop()