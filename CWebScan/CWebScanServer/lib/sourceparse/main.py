#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-02-18 14:27:14
# @Author  : donot (donot@donot.me)
# @Link    : https://blog.donot.me

# 多线程启动消费者 - 原始数据解析
import pika
import pickle
import json
from . import ParseBaseClass
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
from lib.rabbitqueue.initqueue import ToScanQueue
from utils.DataStructure import RequestData

def mainConsumer():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.queue_declare(queue="dataprehandlequeue")

    def callback(ch, method, properties, body):
        postDataJson = json.loads(body)
        chromeType = postDataJson['bodyType']

        try:
            reqHeaders = postDataJson['reqHeaders']
        except Exception as e:
            reqHeaders = {}

        try:
          contentType = reqHeaders['Content-Type']
        except Exception as e:
            contentType = ''

        if chromeType == 'formData' or chromeType == 'raw':
            data = postDataJson['requestBody']
            parseObj = ParseBaseClass.ParseBase(chromeType, contentType, data)
            res = parseObj.parseData()
            if res:
                print(res)
                ToScanQueue.basic_publish(exchange='', routing_key='toscanqueue', body=pickle.dumps(res))
            else:
                pass # log
        else:
            pass # log

    channel.basic_consume(callback, queue='dataprehandlequeue', no_ack=True)
    channel.start_consuming()


if __name__ == '__main__':
    parseTest = ParseBase('formData', 'application/x-www-form-urlencoded; charset=UTF-8', "{\"metadata[]\":[\"\"],\"path\":[\"%2FROOT%2FHOME\"]}")
    parseTest.parseData()
    # parseTest.parse()
