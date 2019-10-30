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
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
from lib.rabbitqueue.consumerBase import ConsumerBase
from lib.rabbitqueue.producerMultiBase import PublisherMultiBase
from utils.DataStructure import RequestData
from utils.globalParam import ScanLogger, CWebScanSetting, ScanTaskVulnType, ScanTaskStatus, DOMAIN_BLACK_LIST
from lib.models.datamodel import ScanTask, HostScan


class DistributeConsumer(ConsumerBase):
    def __init__(self, ampq_url, queue_name, routing_key, q, dbsession):
        super(DistributeConsumer, self).__init__(ampq_url, queue_name, routing_key)
        self.transQueue = q
        self.dbsession = dbsession

    def on_message(self, _unused_channel, basic_deliver, properties, body):
        data = pickle.loads(body)
        ScanLogger.warning('DistributeConsumer received message # %s from %s: %s',
                    basic_deliver.delivery_tag, properties.app_id, data.netloc)
        
        '''
        可重放检查
        '''
        isOk, averageLength = self.repeatCheck(data)
        if isOk:
            pass
        else:
            # self.changeScanStatus(data.scanid)
            ScanLogger.warning('repeatCheck Failed ' + data.netloc)
            self.acknowledge_message(basic_deliver.delivery_tag)
            return

        '''
        内网ip检查
        '''
        if re.match(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$", data.netloc):
            if self.is_internal_ip(data.netloc):
                self.acknowledge_message(basic_deliver.delivery_tag)
                return
            else:
                pass
        else:
            pass

        '''
        域名黑名单检测
        '''
        for black_domain in DOMAIN_BLACK_LIST:
            if black_domain in data.netloc:
                self.acknowledge_message(basic_deliver.delivery_tag)
                return
            else:
                continue


        scanList = []
        isHostScaned = self.hostScanCheck(data.netloc)
        if isHostScaned:
            pass
        else:
            # 进行端口/目录/根目录备份文件 扫描
            # scanList.append('host')
            # scanList.append('dir')
            # scanList.append('file')
            pass

        '''
        此处可对原始数据包进行逻辑判断，以通过设定routing_key而进入不同扫描器的消息队列中
        '''
        if data.dataformat == 'ALLNO':
            scanList.append('sqli') # header 
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
            self.transQueue.put(pickle.dumps({'routing_key': i + 'scan.key', 'body': pickle.dumps(data)}))
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

    def ip_into_int(self, ip):
        # 先把 192.168.1.13 变成16进制的 c0.a8.01.0d ，再去了“.”后转成10进制的 3232235789 即可。
        # (((((192 * 256) + 168) * 256) + 1) * 256) + 13
        return reduce(lambda x,y:(x<<8)+y,map(int,ip.split('.')))

    def is_internal_ip(self, ip):
        ip = self.ip_into_int(ip)
        net_a = self.ip_into_int('10.255.255.255') >> 24
        net_b = self.ip_into_int('172.31.255.255') >> 20
        net_c = self.ip_into_int('192.168.255.255') >> 16
        return ip >> 24 == net_a or ip >>20 == net_b or ip >> 16 == net_c

    def save2db(self, data, vulntype):
        '''
        对扫描数据入库 时间、扫描类型、请求包
        dbname: scantask
        '''
        save2scantask = ScanTask(
            dataid = data.saveid,
            scantype = vulntype,
            netloc = data.netloc,
            status = ScanTaskStatus['running']
        )
        session = self.dbsession()
        session.add(save2scantask)
        session.flush()
        scanid = save2scantask.id
        session.commit()
        session.close()
        return scanid

    def repeatCheck(self, data):
        '''
        可重放检测
        没有Conetent-Length的包不做检测，依赖Cotent-Length进行检测，没有Content-Length暂时不做扫描
        '''
        # url = data.url
        # method = data.method
        if 'Content-Length' in data.reqHeaders:
            src_ctl = data.reqHeaders['Content-Length']
        elif 'content-length' in data.reqHeaders:
            src_ctl = data.reqHeaders['content-length']
        else:
            src_ctl = 0
            NoLength = True
        if NoLength:
            return True, None
        respLengthList = []
        for i in range(3):
            ela, headers = self.reqSendForRepeatCheck(data.url, data.method, data.postData, data.reqHeaders)
            if headers is not None:
                self.respTimeList.append(ela)
                self.timesRcordList.append(ela)
                if 'Content-Length' in headers:
                    respLengthList.append(int(headers['Content-Length']))
                elif 'content-length' in headers:
                    respLengthList.append(int(headers['content-length']))
                else:
                    ctl = -1
            else:
                pass
        if len(respLengthList) > 1:
            averageLength = sum(respLengthList) / len(respLengthList)
        else:
            for i in range(3):
                ela, headers = self.reqSendForRepeatCheck(data.url, data.method, data.postData, data.reqHeaders)
                if headers is not None:
                    self.respTimeList.append(ela)
                    if 'Content-Length' in headers:
                        respLengthList.append(int(headers['Content-Length']))
                    elif 'content-length' in headers:
                        respLengthList.append(int(headers['content-length']))
                    else:
                        ctl = -1
                else:
                    pass

            if len(respLengthList) < 3:
                '''
                可重放性检测失败
                '''
                ScanLogger.warning('reqSendForRepeatCheck success < 3 times')
                return False, None
            else:
                averageLength = sum(respLengthList) / len(respLengthList)

        ration = abs(averageLength - src_ctl) / src_ctl
        if ration < 0.2:
            return True, averageLength
        else:
            ScanLogger.warning('ration > 0.2: ' + data.url)
            return False, averageLength

    def reqSendForRepeatCheck(self, method, url, data, headers):
        s = Session()
        req = Request(method, 
            url = url,
            data = data,
            headers = headers
        )
        prepped = s.prepare_request(req)
        try:
            resp = s.send(prepped, verify=False, timeout=20, allow_redirects=False)
        except Exception as e:
            ScanLogger.warning(e)
            return 0, None
        return resp.elapsed.total_seconds(), resp.headers

    def changeScanStatus(self, scanid, status = ScanTaskStatus['repeat_check_failed']):
        session = self.dbsession()
        scans = session.query(ScanTask).filter_by(id=scanid).all()
        if len(scans) == 1:
            scans[0].status = status
            session.commit()
            session.close()
            # return True
        else:
            ScanLogger.warning('ChangeScanStatus Failed, the scan id not only unique, scanid: %s' % scanid)
            # return False


def distributeMain(q):
    engine = create_engine(CWebScanSetting.MYSQL_URL, pool_size=20, pool_recycle=599, pool_timeout=30)
    DB_Session = sessionmaker(bind=engine)
    example = DistributeConsumer(CWebScanSetting.AMQP_URL, 'distribute', 'distribute.source', q, DB_Session)
    try:
        example.run()
    except KeyboardInterrupt:
        example.stop()

def distributeTrans(q):
    publishmultiObj = PublisherMultiBase(CWebScanSetting.AMQP_URL + "&heartbeat=0", ['sqliscan', 'rcescan'], ['sqliscan.key', 'rcescan.key'], q)
    publishmultiObj.run()