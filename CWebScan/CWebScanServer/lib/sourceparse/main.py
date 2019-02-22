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
import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
from lib.rabbitqueue.initqueue import ToScanQueue
from utils.DataStructure import RequestData
from utils.globalParam import ScanLogger, CWebScanSetting
from lib.models.datamodel import User, data_raw, data_clean

def parseMain():
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

        # 原始数据存储
        # ...
        save2data_raw = data_raw(saveid = postDataJson['InitId']+postDataJson['requestId'], url = postDataJson['url'], method = postDataJson['method'], 
            body=postDataJson['requestBody'], reqHeaders = postDataJson['reqHeaders'], resHeaders = postDataJson['resHeaders'], time = datetime.datetime)
        # print(CWebScanSetting.MysqlSession.execute('show databases').fetchall())

        if chromeType == 'formData' or chromeType == 'raw':
            parseObj = ParseBaseClass.ParseBase(postDataJson['url'], chromeType, contentType, postDataJson['requestBody'])
            res = parseObj.parse()
            if res:
                ScanLogger.info("Parse Source RequestData Successfully!")
            else:
                ScanLogger.error("Not Generate RequestData!")
                return 0
        else:
            parseObj = ParseBaseClass.ParseBase(postDataJson['url'], chromeType, contentType, '')
            res = parseObj.parse()

        res.method = postDataJson['method']
        res.url = postDataJson['url']
        res.resip = postDataJson['resIp']
        res.statuscode = postDataJson['statusCode']
        res.reqHeaders = reqHeaders
        res.resHeaders = postDataJson['resHeaders']
        # print(res.__dict__)

        # 清洗后数据存储
        # ...
        session = CWebScanSetting.DB_Session()
        user = User(name=res.netloc)
        session.add(user)
        session.commit()
        ToScanQueue.basic_publish(exchange='', routing_key='toscanqueue', body=pickle.dumps(res))


    channel.basic_consume(callback, queue='dataprehandlequeue', no_ack=True)
    channel.start_consuming()


if __name__ == '__main__':
    parseTest = ParseBase('formData', 'application/x-www-form-urlencoded; charset=UTF-8', "{\"metadata[]\":[\"\"],\"path\":[\"%2FROOT%2FHOME\"]}")
    parseTest.parseData()

