#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-02-20 17:02:28
# @Author  : donot (donot@donot.me)
# @Link    : https://blog.donot.me

import pickle
import pika
import sys
import os
import requests
from concurrent.futures import ThreadPoolExecutor
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
from lib.rabbitqueue.consumerBase import ConsumerBase

class SqliScanBase(object):
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


class SqliScanConsumer(ConsumerBase):
    def __init__(self, amqp_url, queue_name, routing_key):
        super(ParseConsumer, self).__init__(amqp_url, queue_name, routing_key)
        self.scaning = 0
        self.scaned = 0
        self.pool =  ThreadPoolExecutor(30)

    def on_message(self, unused_channel, basic_deliver, properties, body):
        '''
        重写消息处理方法
        '''
        # data = json.loads(pickle.loads(body))
        # data_parsed = self.parse_message(body)
        # ScanLogger.warning('ParseConsumer Received message # %s from %s: %s',
        #             basic_deliver.delivery_tag, properties.app_id, data_parsed.netloc)
        sqliscanObj = SqliScanBase(body)
        sqliscanObjfeaeture = self.pool.submit(sqliscanObj.run)
        sqliscanObj.add_done_callback(self.threadcallback)
        self.scaning = self.scaning + 1
        if :
            pass
        self.acknowledge_message(basic_deliver.delivery_tag)

    def threadcallback(self):
        self.scaning = self.scaning - 1
        self.scaned = self.scaned + 1



def SqliScanMain():
    example = SqliScanConsumer('amqp://guest:guest@localhost:5672/%2F', 'sqliscan', 'sqliscan.source')
    try:
        example.run()
    except KeyboardInterrupt:
        example.stop()