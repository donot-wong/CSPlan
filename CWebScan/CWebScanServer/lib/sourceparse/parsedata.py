#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-02-18 14:27:14
# @Author  : donot (donot@donot.me)
# @Link    : https://blog.donot.me

# 多线程启动消费者 - 原始数据解析
import pika
import pickle
import json
from urllib import parse
import sys
import os
from . import ParseBaseClass
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
from lib.rabbitqueue.consumerBase import ConsumerBase
from lib.rabbitqueue.producerBase import PublisherBase
from utils.DataStructure import RequestData
from utils.globalParam import ScanLogger, CWebScanSetting
from lib.models.datamodel import data_raw, data_clean


class ParseConsumer(ConsumerBase):
    TransQUEUE = None
    def __init__(self, amqp_url, queue_name, routing_key, q, dbsession):
        super(ParseConsumer, self).__init__(amqp_url, queue_name, routing_key)
        self.TransQUEUE = q
        self.dbsession = dbsession

    def on_message(self, unused_channel, basic_deliver, properties, body):
        '''
        重写消息处理方法
        '''
        scanflag = True
        data_parsed = self.parse_message(body)
        if data_parsed.method == 'GET' and data_parsed.query == '':
            scanflag = False
        elif data_parsed.method == 'POST' and data_parsed.body == '' and data_parsed.query == '':
            scanflag = False
        elif data_parsed.statuscode >= 400:
            scanflag = False
        ScanLogger.warning('ParseConsumer Received message # %s from %s: %s',
                    basic_deliver.delivery_tag, properties.app_id, data_parsed.netloc)
        self.acknowledge_message(basic_deliver.delivery_tag)
        if scanflag is True:
            self.TransQUEUE.put(pickle.dumps(data_parsed))

    def parse_message(self, body):
        postDataJson = json.loads(pickle.loads(body))
        try:
            chromeType = postDataJson['bodyType']
        except Exception as e:
            ScanLogger.error('access bodyType error! ' + postDataJson['url'])
            return 0

        try:
            reqHeaders = postDataJson['reqHeaders']
        except Exception as e:
            reqHeaders = {}

        try:
          contentType = reqHeaders['Content-Type']
        except Exception as e:
            contentType = ''

        # print(reqHeaders)
        try:
            cookie = reqHeaders['Cookie']
        except Exception as e:
            cookie = ''
        # Referer Origin User-Agent Accept-Language Accept-Encoding Accept
        # 原始数据存储
        # ...
        save2data_raw = data_raw(
            saveid = postDataJson['InitId'] + postDataJson['requestId'], 
            url = postDataJson['url'], 
            method = postDataJson['method'], 
            body = parse.quote(postDataJson['requestBody']) if chromeType not in ['empty','error'] else '' , 
            reqheaders = parse.quote(str(postDataJson['reqHeaders'])), 
            resheaders = parse.quote(str(postDataJson['resHeaders']))
        )

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

        res.cookie = cookie
        res.ct = contentType
        res.method = postDataJson['method']
        res.url = postDataJson['url']
        try:
            res.resip = postDataJson['resIp']
        except Exception as e:
            res.resip = ''
        
        res.saveid = postDataJson['InitId'] + postDataJson['requestId']
        res.statuscode = postDataJson['statusCode']
        res.reqHeaders = reqHeaders
        res.resHeaders = postDataJson['resHeaders']
        # print(res.__dict__)

        # 清洗后数据存储
        # ...

        save2data_clean = data_clean(
            saveid = res.saveid, 
            netloc = res.netloc,
            scheme = res.scheme,
            method = res.method,
            path = res.path,
            query = res.query,
            body = parse.quote(str(res.postData)) if chromeType not in ['empty','error'] else '',
            ct = res.contentType,
            cookie = res.cookie,
            reqheaders = parse.quote(str(res.reqHeaders)),
            resheaders = parse.quote(str(res.resHeaders)),
            statuscode = res.statuscode
        )
        ScanLogger.warning('ParseConsumer handle message # %s start...', res.saveid)
        try:
            session = self.dbsession()
            session.add(save2data_raw)
            session.add(save2data_clean)
            session.commit()
        except Exception as e:
            raise e
        return res

def parseMain(q):
    engine = create_engine('mysql+pymysql://root:123456@127.0.0.1:3306/test')
    DB_Session = sessionmaker(bind=engine)
    example = ParseConsumer('amqp://guest:guest@localhost:5672/%2F', 'parsesrcdata', 'parsesrcdata.source', q, DB_Session)
    try:
        example.run()
    except KeyboardInterrupt:
        example.stop()


def trans2distribute(q):
    example = PublisherBase('amqp://guest:guest@localhost:5672/%2F?connection_attempts=3&heartbeat_interval=3600', 'distribute', 'distribute.source', q)
    example.run()

# if __name__ == '__main__':
#     parseTest = ParseBase('formData', 'application/x-www-form-urlencoded; charset=UTF-8', "{\"metadata[]\":[\"\"],\"path\":[\"%2FROOT%2FHOME\"]}")
#     parseTest.parseData()

