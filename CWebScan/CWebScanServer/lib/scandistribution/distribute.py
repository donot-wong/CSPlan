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
from lib.models.datamodel import ScanTask


class DistributeConsumer(ConsumerBase):
    def __init__(self, ampq_url, queue_name, routing_key, q, dbsession):
        super(DistributeConsumer, self).__init__(ampq_url, queue_name, routing_key)
        self.transQueue = q
        self.dbsession = dbsession

    def on_message(self, unused_channel, basic_deliver, properties, body):
        data = pickle.loads(body)
        ScanLogger.warning('DistributeConsumer received message # %s from %s: %s',
                    basic_deliver.delivery_tag, properties.app_id, data.netloc)

        scanid_sqli = self.save2db(data, ScanTaskVulnType['sqli'])
        scanid_rce = self.save2db(data, ScanTaskVulnType['rce'])
        ScanLogger.warning('DistributeConsumer generate scanid %s' % scanid_sqli)
        ScanLogger.warning('DistributeConsumer generate scanid %s' % scanid_rce)
        data.scanid = scanid_sqli
        self.transQueue.put({'routing_key': 'sqliscan.key', 'body': pickle.dumps(data)})
        data.scanid = scanid_rce
        self.transQueue.put({'routing_key': 'rcescan.key', 'body': pickle.dumps(data)})
        self.acknowledge_message(basic_deliver.delivery_tag)

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