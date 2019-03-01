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

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
from lib.rabbitqueue.consumerBase import ConsumerBase
from utils.globalParam import ScanLogger
from utils.DataStructure import RequestData

class RceScanBase(object):
    """docstring for SqliScanBase"""
    SrcRequest = None
    def __init__(self, request):
        self.SrcRequest = request
    
    def run(self):
        '''
        线程中调用的函数
        '''
        pass

    def function():
        pass


class RceScanConsumer(ConsumerBase):
    def __init__(self, amqp_url, queue_name, routing_key):
        super(RceScanConsumer, self).__init__(amqp_url, queue_name, routing_key)
        self.scaning = 0
        self.scaned = 0
        self.pool =  ThreadPoolExecutor(30)

    def on_message(self, unused_channel, basic_deliver, properties, body):
        '''
        重写消息处理方法
        '''
        data = pickle.loads(body)
        ScanLogger.warning('RceScanConsumer Received message # %s from %s: %s',
                    basic_deliver.delivery_tag, properties.app_id, data.netloc)
        self.acknowledge_message(basic_deliver.delivery_tag)
        # sqliscanObj = SqliScanBase(body)
        # sqliscanObjfeaeture = self.pool.submit(sqliscanObj.run)
        # sqliscanObj.add_done_callback(self.threadcallback)
        # self.scaning = self.scaning + 1
        # self.acknowledge_message(basic_deliver.delivery_tag)
        # while self.scaning > 35:
        #     ScanLogger.warning("SqliScanConsumer ThreadPool more than 30, now: {scaningnum}".format(scaningnum=self.scaning))
        #     time.sleep(3)

    def threadcallback(self):
        self.scaning = self.scaning - 1
        self.scaned = self.scaned + 1



def RceScanMain():
    example = RceScanConsumer('amqp://guest:guest@localhost:5672/%2F', 'rcescan', 'rcescan.key')
    try:
        example.run()
    except KeyboardInterrupt:
        example.stop()