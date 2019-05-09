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
import hashlib
from . import ParseBaseClass
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
from lib.rabbitqueue.consumerBase import ConsumerBase
from lib.rabbitqueue.producerBase import PublisherBase
from utils.DataStructure import RequestData
from utils.globalParam import ScanLogger, CWebScanSetting, BlackParamName
from lib.models.datamodel import data_raw, data_clean, data_clean_key


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

        data_parsed = self.parse_message(body)
        if data_parsed is None:
            self.acknowledge_message(basic_deliver.delivery_tag)
        else:
            ScanLogger.warning('ParseConsumer Received message # %s from %s: %s',
                        basic_deliver.delivery_tag, properties.app_id, data_parsed.netloc)
            self.acknowledge_message(basic_deliver.delivery_tag)
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
            reqheaders = parse.quote(str(reqHeaders)), 
            resheaders = parse.quote(str(postDataJson['resHeaders']))
        )

        if chromeType in ['formData', 'raw']:
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

        if res.dataformat == 'UNKNOWN':
            '''
            数据格式解析失败，应存储在解析失败数据库
            '''
            session = self.dbsession()
            save2data_raw.parsestatus = 0
            session.add(save2data_raw)
            session.commit()
            session.close()
            return None
        elif postDataJson['statusCode'] >= 400:
            session = self.dbsession()
            save2data_raw.parsestatus = 2
            session.add(save2data_raw)
            session.commit()
            session.close()
            return None
        else:
            pass

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

        if chromeType in ['empty','error']:
            res.postData = ''

        key1raw = res.scheme + res.method + res.netloc + res.path
        key1 = hashlib.md5(key1raw.encode('utf-8')).hexdigest()

        if res.dataformat == 'NOBODY':
            keytype = 1
            key2raw = ''
            for key,value in res.getData.items():
                key2raw = key2raw + key
            key2 = hashlib.md5(key2raw.encode('utf-8')).hexdigest()
        elif res.dataformat == 'FORMDATA':
            keytype = 1
            key2raw = ''
            for key,value in res.postData.items():
                key2raw = key2raw + key
            key2 = hashlib.md5(key2raw.encode('utf-8')).hexdigest()
        elif res.dataformat == 'JSON':
            keytype = 1
            key2raw = ''
            try:
                for key,value in json.loads(res.postData).items():
                    key2raw = key2raw + key
                key2 = hashlib.md5(key2raw.encode('utf-8')).hexdigest()
            except Exception as e:
                key2 = ''      
        elif res.dataformat == 'ALLNO':
            keytype = 2
            key2 = ''
            key1 = self.genUrlKey(res.url)
        else:
            keytype = 2
            key2 = ''
            key1 = self.genUrlKey(res.url)

        if 'Content-Type' in res.resHeaders:
            key3 = res.resHeaders['Content-Type']
        elif 'content-type' in res.resHeaders:
            key3 = res.resHeaders['content-type']
        else:
            key3 = ''

        if 'Content-Length' in res.resHeaders:
            key4 = int(res.resHeaders['Content-Length'])
        elif 'content-length' in res.resHeaders:
            key4 = int(res.resHeaders['content-length'])
        else:
            key4 = 0

        checkRes = self.checkSourceData(keytype, key1, key2, key3, key4)
        if checkRes:
            save2data_clean_key = data_clean_key(
                keytype = keytype,
                key1 = key1,
                key2 = key2,
                key3 = key3,
                key4 = key4,
                key5 = ''
            )
        else:
            '''
            未通过
            '''
            return None

        # 清洗后数据存储
        # ...

        save2data_clean = data_clean(
            saveid = res.saveid, 
            netloc = res.netloc,
            scheme = res.scheme,
            method = res.method,
            path = res.path,
            query = res.query,
            body = parse.quote(json.dumps(res.postData)),
            ct = res.ct,
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
            session.flush()
            save2data_raw.parsestatus = 1
            save2data_clean_key.dataid = save2data_clean.id
            session.add(save2data_clean_key)
            session.commit()
            session.close()
        except Exception as e:
            raise e
        return res

    def genUrlKey(self, url):
        o = parse.urlparse(url)
        # self.ret.scheme = o.scheme
        # self.ret.netloc = o.netloc
        # self.ret.path = o.path
        # self.ret.query = o.query
        path = o.path
        if len(path.split('/')[-1].split('.')) > 1:
            tail = path.split('/')[-1].split('.')[-1]
        elif len(path.split('/')) == 1:
            tail = path
        else:
            tail = '1'

        tail = tail.lower()
        path_length = len(path.split('/')) - 1
        path_value = 0
        path_list = path.split('/')[:-1] + [tail]

        for i in range(path_length + 1):
            if path_length -i == 0:
                path_value_end = str(path_value) + str(hashlib.md5(path_list[path_length - i].encode('utf-8')))
            else:
                path_value += len(path_list[path_length - i]) * (10**(i+1))
        netloc_value = hashlib.md5(o.netloc.encode('utf-8')).hexdigest()
        url_value = hashlib.md5((str(path_value)+str(netloc_value)).encode('utf-8')).hexdigest()
        return url_value


    def checkSourceData(self, keytype, key1, key2, key3, key4):
        '''
        检测这个包是不是需要被存储并下发扫描
        return: True/False(不存在可匹配数据/存在可匹配数据)
        '''
        session = self.dbsession()
        if keytype == 1:
            searchByKey1Res = session.query(data_clean_key).filter_by(key1=key1).all()
            session.close()
            if len(searchByKey1Res) == 0:
                return True
            else:
                for i in searchByKey1Res:
                    if i.key2 == key2:
                        if i.key3 == key3:
                            if i.key4 == 0 and key4 == 0:
                                return False
                            elif i.key4 == 0 and key4 != 0:
                                continue
                            else:
                                ration = abs(i.key4 - key4) / i.key4
                                if ration > 0.2:
                                    continue
                                else:
                                    return False
                        else:
                            continue
                    else:
                        continue
                return True
        elif keytype == 2:
            urlkey = key1
            searchByKey1Res = session.query(data_clean_key).filter_by(key1=key1).all()
            session.close()
            if len(searchByKey1Res) == 0:
                return True
            else:
                for i in searchByKey1Res:
                    if i.key3 == key3:
                        if i.key4 == 0 and key4 == 0:
                            return False
                        elif i.key4 == 0 and key4 != 0:
                            continue
                        else:
                            ration = abs(i.key4 - key4) / i.key4
                            if ration > 0.4:
                                continue
                            else:
                                return False
                    else:
                        continue
                return True
            return True

def parseMain(q):
    engine = create_engine('mysql+pymysql://root:123456@127.0.0.1:3306/test', pool_size=20, pool_recycle=599, pool_timeout=30)
    DB_Session = sessionmaker(bind=engine)
    parseCS = ParseConsumer('amqp://guest:guest@localhost:5672/%2F', 'parsesrcdata', 'parsesrcdata.source', q, DB_Session)
    try:
        parseCS.run()
    except KeyboardInterrupt:
        parseCS.stop()


def trans2distribute(q):
    publish2distribueObj = PublisherBase('amqp://guest:guest@localhost:5672/%2F?connection_attempts=3&heartbeat_interval=3600', 'distribute', 'distribute.source', q)
    publish2distribueObj.run()

# if __name__ == '__main__':
#     parseTest = ParseBase('formData', 'application/x-www-form-urlencoded; charset=UTF-8', "{\"metadata[]\":[\"\"],\"path\":[\"%2FROOT%2FHOME\"]}")
#     parseTest.parseData()

