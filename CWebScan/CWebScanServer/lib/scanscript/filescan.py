#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-05-15 18:13:51
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
from utils.globalParam import ScanLogger,  BlackParamName, BLACK_COOKIE_KEY_LIST, BLACK_HTTP_HEADER_KEY_LIST, ScanTaskStatus, VulnType, AlertTemplateDict, CalcAverageTimeLimitCnt
from utils.globalParam import TIME_STDEV_COEFF, MIN_VALID_DELAYED_RESPONSE
from utils.DataStructure import RequestData
from lib.scanscript.sqliscan.errorbased import plainArray, regexArray
from lib.models.datamodel import ScanTask, VulnData
from utils.commonFunc import send2slack
from lib.scanscript.scanBase import ScanBase

class FileScan(ScanBase):
    SrcRequest = None
    def __init__(self, request, dbsession):
        super(FileScan, self).__init__(request, dbsession)

    def run():
    	pass
		


class FileScanConsumer(ConsumerBase):
    def __init__(self, amqp_url, queue_name, routing_key, dbsession):
        super(FileScanConsumer, self).__init__(amqp_url, queue_name, routing_key)
        self.scaning = 0
        self.scaned = 0
        self.pool =  ThreadPoolExecutor(max_workers=30)
        self.dbsession = dbsession


    def on_message(self, unused_channel, basic_deliver, properties, body):
        '''
        重写消息处理方法
        '''
        data = pickle.loads(body)
        ScanLogger.warning('FileScanConsumer Received message # %s from %s: %s',
                    basic_deliver.delivery_tag, properties.app_id, data.netloc)
        self.acknowledge_message(basic_deliver.delivery_tag)
        filescanObj = FileScan(data, self.dbsession)
        filescanObjfeaeture = self.pool.submit(filescanObj.run)
        self.scaning = self.scaning + 1
        ScanLogger.warning("FileScanConsumer commit scantask, taskid: %s, now total scaning task: %s" % (data.scanid, self.scaning))
        filescanObjfeaeture.add_done_callback(self.threadcallback)
        while self.scaning > 35:
            ScanLogger.warning("FileScanConsumer ThreadPool more than 30, now: {scaningnum}".format(scaningnum=self.scaning))
            time.sleep(3)

    def threadcallback(self, obj):
        print(obj.result())
        ScanLogger.warning("FileScanConsumer task callback, now total scaning task: %s, scaned task: %s" % (self.scaning, self.scaned))
        self.scaning = self.scaning - 1
        self.scaned = self.scaned + 1


def FileScanMain():
    engine = create_engine('mysql+pymysql://root:123456@127.0.0.1:3306/test', pool_size=20, pool_recycle=599, pool_timeout=30)
    DB_Session = sessionmaker(bind=engine)
    filescan = FileScanConsumer('amqp://guest:guest@localhost:5672/%2F', 'filescan', 'filescan.key', DB_Session)
    try:
        filescan.run()
    except KeyboardInterrupt:
        filescan.stop()
