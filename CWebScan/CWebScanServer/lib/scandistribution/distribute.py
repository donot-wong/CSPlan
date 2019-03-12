#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-02-19 15:30:05
# @Author  : donot (donot@donot.me)
# @Link    : https://blog.donot.me
import pickle
import pika
import sys
import json
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
from lib.rabbitqueue.consumerBase import ConsumerBase
from lib.rabbitqueue.producerMultiBase import PublisherMultiBase
from utils.DataStructure import RequestData
from utils.globalParam import ScanLogger, CWebScanSetting, ScanTaskVulnType, ScanTaskStatus
from lib.models.datamodel import ScanTask, HostScan


class DistributeConsumer(ConsumerBase):
    def __init__(self, ampq_url, queue_name, routing_key, q, dbsession):
        super(DistributeConsumer, self).__init__(ampq_url, queue_name, routing_key)
        self.transQueue = q
        self.dbsession = dbsession

    def on_message(self, unused_channel, basic_deliver, properties, body):
        data = pickle.loads(body)
        ScanLogger.warning('DistributeConsumer received message # %s from %s: %s',
                    basic_deliver.delivery_tag, properties.app_id, data.netloc)

        '''
        此处可对原始数据包进行逻辑判断，以通过设定routing_key而进入不同扫描器的消息队列中

        '''
        scanList = []
        isHostScaned = self.hostScanCheck(data.netloc)
        if isHostScaned:
            pass
        else:
            # 进行端口/目录/根目录备份文件 扫描
            # scanList.append('hostscan')
            # scanList.append('dirscan')
            # scanList.append('filescan')
            pass
        if data.dataformat == 'ALLNO':
            # self.acknowledge_message(basic_deliver.delivery_tag)
            pass
            # 没有query/body的情况
        elif data.dataformat == 'FORMDATA':
            scanList.append('sqli')
            scanList.append('rce')
            # 注入
            # RCE
            # XSS
            # 
        elif data.dataformat == 'JSON':
            scanList.append('sqli')
            scanList.append('rce')
            # scanList.append('fastjson')
            # fastjson
            # 注入
            # rce
        elif data.dataformat == 'XML':
            # scanList.append('xxe')
            if data.query != '':
                scanList.append('sqli')
                scanList.append('rce')
            # xxe
        elif data.dataformat == 'MULTIPART':
            scanList.append('sqli')
            scanList.append('rce')
            # scanList.append('file')
            # 文件上传
            # 注入
            # rce
        elif data.dataformat == 'NOBODY':
            if data.query != '':
                scanList.append('sqli')
                scanList.append('rce')
            else:
                # self.acknowledge_message(basic_deliver.delivery_tag)
                pass
            # 注入
            # RCE
            # XSS
        else:
            pass

        for i in scanList:
            scanid = self.save2db(data, ScanTaskVulnType[i])
            data.scanid = scanid
            self.transQueue.put({'routing_key': i+'scan.key', 'body': pickle.dumps(data)})
        self.acknowledge_message(basic_deliver.delivery_tag)

    def hostScanCheck(self, netloc):
        if ':' in netloc:
            host = netloc.split(':')[0]
        else:
            host = netloc
        session = self.dbsession()
        ss = session.query(HostScan).filter_by(host=host).all()
        if len(ss) > 0:
            ret = True
        else:
            hostscan = HostScan(host=host)
            session.add(hostscan)
            session.commit()
            ret = False
        session.close()
        return ret

    def save2db(self, data, vulntype):
        '''
        对扫描数据入库 时间、扫描类型、请求包
        dbname: scantask
        '''
        save2scantask = ScanTask(
            dataid = data.saveid,
            scantype = vulntype,
            status = ScanTaskStatus['running']
        )
        session = self.dbsession()
        session.add(save2scantask)
        session.flush()
        scanid = save2scantask.id
        session.commit()
        session.close()
        return scanid


def distributeMain(q):
    engine = create_engine('mysql+pymysql://root:123456@127.0.0.1:3306/test',pool_size=20)
    DB_Session = sessionmaker(bind=engine)
    example = DistributeConsumer('amqp://guest:guest@localhost:5672/%2F', 'distribute', 'distribute.source', q, DB_Session)
    try:
        example.run()
    except KeyboardInterrupt:
        example.stop()

def distributeTrans(q):
    publishmultiObj = PublisherMultiBase('amqp://guest:guest@localhost:5672/%2F?connection_attempts=3&heartbeat_interval=3600', ['sqliscan', 'rcescan'], ['sqliscan.key', 'rcescan.key'], q)
    publishmultiObj.run()