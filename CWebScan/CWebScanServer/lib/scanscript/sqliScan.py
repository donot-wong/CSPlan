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
import re
from requests import Request, Session
import time
import copy
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
from lib.rabbitqueue.consumerBase import ConsumerBase
from utils.globalParam import ScanLogger,  BlackParamName, BLACK_COOKIE_KEY_LIST, ScanTaskStatus, VulnType, AlertTemplateDict, CalcAverageTimeLimitCnt
from utils.globalParam import TIME_STDEV_COEFF, MIN_VALID_DELAYED_RESPONSE
from utils.DataStructure import RequestData
from lib.scanscript.sqliscan.errorbased import plainArray, regexArray
from lib.models.datamodel import ScanTask, VulnData
from utils.commonFunc import send2slack
from utils.payloads import SQLiPayload_Sleep, SQLiPayload_Sleep_Normal, SQLiPayload_ErrorBased
from lib.scanscript.scanBase import ScanBase


class SqliScan(ScanBase):
    """docstring for SqliScanBase"""
    SrcRequest = None
    def __init__(self, request, dbsession):
        super(SqliScan, self).__init__(request, dbsession)
        # ScanLogger.warning('__init__ called SqliScanBase')
        self.delayTimeJudgeStandard = None

    def run(self):
        '''
        线程中调用的函数
        '''
        # ScanLogger.warning('run called SqliScanBase')
        self.init()

        if self.dataformat == 'NOBODY':
            for key, value in self.getData.items():
                if key not in BlackParamName:
                    hasErrorSqliVuln = self.errorbased('params', key)
                    if hasErrorSqliVuln:
                        self.saveScanResult(VulnType['sqli-error'], key)
                        continue
                    else:
                        hasTimeSqliVuln = self.timebased('params', key)
                        if hasTimeSqliVuln:
                            self.saveScanResult(VulnType['sqli-time'], key)
                            continue
                        else:
                            continue
                else:
                    continue
        elif self.dataformat == 'FORMDATA':
            for key, value in self.postData.items():
                if key not in BlackParamName:
                    hasErrorSqliVuln = self.errorbased('data', key)
                    if hasErrorSqliVuln:
                        self.saveScanResult(VulnType['sqli-error'], key)
                        continue
                    else:
                        hasTimeSqliVuln = self.timebased('data', key)
                        if hasTimeSqliVuln:
                            self.saveScanResult(VulnType['sqli-time'], key)
                            continue
                        else:
                            continue
                else:
                    continue
        elif self.dataformat == 'JSON':
            self.jsondata = json.loads(self.postData)
            try:
                for key, value in self.jsondata.items():
                    if key not in BlackParamName:
                        hasErrorSqliVuln = self.errorbased('data', key)
                        if hasErrorSqliVuln:
                            self.saveScanResult(VulnType['sqli-error', key])
                            continue
                        else:
                            hasTimeSqliVuln = self.timebased('data', key)
                            if hasTimeSqliVuln:
                                self.saveScanResult(VulnType['sqli-time'], key)
                                continue
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


        # 其他含get参数的情况
        if self.dataformat in ['FORMDATA', 'JSON'] and self.getData != {}:
            for key, value in self.getData.items():
                if key not in BlackParamName:
                    hasErrorSqliVuln = self.errorbased('params', key)
                    if hasErrorSqliVuln:
                        self.saveScanResult(VulnType['sqli-error'], key)
                        continue
                    else:
                        hasTimeSqliVuln = self.timebased('params', key)
                        if hasTimeSqliVuln:
                            self.saveScanResult(VulnType['sqli-time', time])
                            continue
                else:
                    continue
        else:
            pass

        if len(self.cookie) > 0:
            for key in self.cookieDict:
                if key != 'other':
                    for black_cookie_key in BLACK_COOKIE_KEY_LIST:
                        if black_cookie_key.lower() in key:
                            flag = True
                            break
                    if flag:
                        continue
                    else:
                        isVuln = self.headerSqliScan(key)
                        if isVuln:
                            self.saveScanResult(VulnType['sqli'], 'Cookie: ' + key)
                            continue
        # referer cookie header注入扫描


        self.changeScanStatus()

    def headerSqliScan(self, key):
        _cookie = copy.copy(self.cookieDict)
        for error_payload in SQLiPayload_ErrorBased:
            _cookie[key] = _cookie[key] + error_payload
            cookieStr = self.cookieDict2Str(_cookie)
            _header = self.SrcRequestHeaders['Cookie'] = 
            res = self.reqSend('header',header=)


    def errorbased(self, loc, key):
        '''
        基于报错的注入扫描
        '''
        if loc == 'params':
            _getData = copy.copy(self.getData)
            _getData[key] = str(_getData[key]) + '\'"'
            res = self.reqSend(loc, _getData, self.url, self.method, self.cookie, self.ua, self.ct, self.SrcRequestHeaders)
            self.sendreqCnt += 1
            return self.checkIsErrorBaseSqli(res)
        elif self.dataformat == 'FORMDATA':
            _postData = copy.copy(self.postData)
            _postData[key] = str(_postData[key]) + '\'"'
            res = self.reqSend(loc, _postData, self.url, self.method, self.cookie, self.ua, self.ct, self.SrcRequestHeaders)
            self.sendreqCnt += 1
            return self.checkIsErrorBaseSqli(res)
        elif self.dataformat == 'JSON':
            _postData = copy.copy(self.jsondata)
            _postData[key] = str(_postData[key]) + '\'"'
            res = self.reqSend(loc, json.dumps(_postData), self.url, self.method, self.cookie, self.ua, self.ct, self.SrcRequestHeaders)
            self.sendreqCnt += 1
            return self.checkIsErrorBaseSqli(res)
        else:
            ScanLogger.warning('Can not handle this request\'s method: %s' % self.method)
            return False

    def timebased(self, loc, key):
        '''
        基于时间延迟注入扫描
        '''

        if self.delayMinTimeCalc():
            # print('delayTimeJudgeStandard: %s' % self.delayTimeJudgeStandard)
            pass
        else:
            return False
        if loc == 'params':
            for payload_idx in range(len(SQLiPayload_Sleep)):
                _getData = copy.copy(self.getData)
                _getData[key] = str(_getData[key]) + SQLiPayload_Sleep[payload_idx].format(sleep='sleep(2)')
                res = self.reqSend(loc, _getData, self.url, self.method, self.cookie, self.ua, self.ct, self.SrcRequestHeaders)
                self.sendreqCnt += 1
                if res is None:
                    continue
                # print('一次时间延迟检测： %s' % res.elapsed.total_seconds())
                if res.elapsed.total_seconds() >= max(MIN_VALID_DELAYED_RESPONSE, self.delayTimeJudgeStandard):
                    if self.twiceCheckForTimeBased(loc, key, payload_idx, res.elapsed):
                        return True
                    else:
                        continue
                else:
                    continue
        elif self.dataformat == 'FORMDATA':
            for payload_idx in range(len(SQLiPayload_Sleep)):
                _postData = copy.copy(self.postData)
                _postData[key] = str(_postData[key]) + SQLiPayload_Sleep[payload_idx].format(sleep='sleep(2)')
                res = self.reqSend(loc, _postData, self.url, self.method, self.cookie, self.ua, self.ct, self.SrcRequestHeaders)
                self.sendreqCnt += 1
                if  res is None:
                    continue
                if res.elapsed.total_seconds() > max(MIN_VALID_DELAYED_RESPONSE, self.delayTimeJudgeStandard):
                    if self.twiceCheckForTimeBased(loc, key, payload_idx, res.elapsed.total_seconds()):
                        return True
                    else:
                        continue
                else:
                    continue
        elif self.dataformat == 'JSON':
            for payload_idx in range(len(SQLiPayload_Sleep)):
                _postData = copy.copy(self.jsondata)
                _postData[key] = str(_postData[key]) + SQLiPayload_Sleep[payload_idx].format(sleep='sleep(2)')
                res = self.reqSend(loc, json.dumps(_postData), self.url, self.method, self.cookie, self.ua, self.ct, self.SrcRequestHeaders)
                self.sendreqCnt += 1
                if res is None:
                    continue
                if res.elapsed.total_seconds() > max(MIN_VALID_DELAYED_RESPONSE, self.delayTimeJudgeStandard):
                    if self.twiceCheckForTimeBased(loc, key, payload_idx, res.elapsed.total_seconds()):
                        return True
                    else:
                        continue
                else:
                    continue
        else:
            ScanLogger.warning('Can not handle this request\'s method: %s' % self.method)
            return False

    def twiceCheckForTimeBased(self, loc, key, payload_idx, onceela):
        '''
        时间盲注一次检出后二次确认
        '''
        ela, _ = self.reqSendForRepeatCheck()
        if ela >= max(MIN_VALID_DELAYED_RESPONSE, self.delayTimeJudgeStandard):
            # print('twiceCheckForTimeBased Failed, els: %s' % ela)
            return False
        else:
            if loc == 'params':
                _getData = copy.copy(self.getData)
                # 进行一次不发生时间延迟payload检测
                _getData[key] = str(_getData[key]) + SQLiPayload_Sleep_Normal[payload_idx]
                res = self.reqSend(loc, _getData, self.url, self.method, self.cookie, self.ua, self.ct, self.SrcRequestHeaders)
                self.sendreqCnt += 1
                if res.elapsed.total_seconds() < max(MIN_VALID_DELAYED_RESPONSE, self.delayTimeJudgeStandard):
                    # 进行一次时间延迟注入payload检测
                    _getData[key] = str(self.getData[key]) + SQLiPayload_Sleep[payload_idx].format(sleep='sleep(2)')
                    res = self.reqSend(loc, _getData, self.url, self.method, self.cookie, self.ua, self.ct, self.SrcRequestHeaders)
                    self.sendreqCnt += 1
                    # print('二次检测响应时间： %s' % res.elapsed.total_seconds())
                    if res.elapsed.total_seconds() >= max(MIN_VALID_DELAYED_RESPONSE, self.delayTimeJudgeStandard):
                        return True
                    else:
                        return False
                else:
                    return False
            elif self.dataformat == 'FORMDATA':
                _postData = copy.copy(self.postData)
                _postData[key] = str(_postData[key]) + SQLiPayload_Sleep_Normal[payload_idx]
                res = self.reqSend(loc, _postData, self.url, self.method, self.cookie, self.ua, self.ct, self.SrcRequestHeaders)
                self.sendreqCnt += 1
                if res.elapsed.total_seconds() < max(MIN_VALID_DELAYED_RESPONSE, self.delayTimeJudgeStandard):
                    _postData[key] = str(self.postData[key]) + SQLiPayload_Sleep[payload_idx].format(sleep='sleep(2)')
                    res = self.reqSend(loc, _postData, self.url,self.method, self.cookie, self.ua, self.ct, self.SrcRequestHeaders)
                    self.sendreqCnt += 1
                    if res.elapsed.total_seconds() >= max(MIN_VALID_DELAYED_RESPONSE, self.delayTimeJudgeStandard):
                        return True
                    else:
                        return False
                else:
                    return False
            elif self.dataformat == 'JSON':
                _postData = copy.copy(self.jsondata)
                _postData[key] = str(_postData[key]) + SQLiPayload_Sleep_Normal[payload_idx]
                res = self.reqSend(loc, json.dumps(_postData), self.url, self.method, self.cookie, self.ua, self.ct, self.SrcRequestHeaders)
                self.sendreqCnt += 1
                if res.elapsed.total_seconds() <  max(MIN_VALID_DELAYED_RESPONSE, self.delayTimeJudgeStandard):
                    _postData[key] = str(self.jsondata[key]) + SQLiPayload_Sleep[payload_idx].format(sleep='sleep(2)')
                    res = self.reqSend(loc, json.dumps(_postData), self.url, self.method, self.cookie, self.ua, self.ct, self.SrcRequestHeaders)
                    self.sendreqCnt += 1
                    if res.elapsed.total_seconds() >= max(MIN_VALID_DELAYED_RESPONSE, self.delayTimeJudgeStandard):
                        return True
                    else:
                        return False
                else:
                    return False
            else:
                return False

    def delayMinTimeCalc(self):
        '''
        计算时间盲注时间判断基准
        '''
        cnt = 0
        while len(self.respTimeList) < CalcAverageTimeLimitCnt:
            ela, headers = self.reqSendForRepeatCheck()
            cnt += 1
            if ela != 0 and headers is not None:
                self.respTimeList.append(ela)
            if cnt > 20:
                break
        # print(self.respTimeList)
        min_resp_time = min(self.respTimeList)
        average_resp_time = sum(self.respTimeList) / len(self.respTimeList)
        _ = 0
        for i in self.respTimeList:
            _ += (i - average_resp_time)**2
        deviation = (_ / (len(self.respTimeList) - 1)) ** 0.5
        self.delayTimeJudgeStandard = average_resp_time + TIME_STDEV_COEFF * deviation
        # print('时间延时基准计算完成: %s' % self.delayTimeJudgeStandard)
        return True


    def checkIsErrorBaseSqli(self, res):
        '''
        报错注入 报错内容检测
        '''
        if res is None:
            return False
        else:
            dr = re.compile(r'<[^>]+>',re.S)
            dd = dr.sub('', res.text)
        for i in plainArray:
            if i in dd:
                ScanLogger.warning('SqliScanBase checkIsErrorBaseSqli function: find sqli base condition %s' % i)
                return True
        return False


class SqliScanConsumer(ConsumerBase):
    def __init__(self, amqp_url, queue_name, routing_key, dbsession):
        super(SqliScanConsumer, self).__init__(amqp_url, queue_name, routing_key)
        self.scaning = 0
        self.scaned = 0
        self.pool =  ThreadPoolExecutor(max_workers=30)
        self.dbsession = dbsession


    def on_message(self, unused_channel, basic_deliver, properties, body):
        '''
        重写消息处理方法
        '''
        data = pickle.loads(body)
        ScanLogger.warning('SqliScanConsumer Received message # %s from %s: %s',
                    basic_deliver.delivery_tag, properties.app_id, data.netloc)
        self.acknowledge_message(basic_deliver.delivery_tag)
        sqliscanObj = SqliScan(data, self.dbsession)
        sqliscanObjfeaeture = self.pool.submit(sqliscanObj.run)
        self.scaning = self.scaning + 1
        ScanLogger.warning("SqliScanConsumer commit scantask, taskid: %s, now total scaning task: %s" % (data.scanid, self.scaning))
        sqliscanObjfeaeture.add_done_callback(self.threadcallback)
        while self.scaning > 35:
            ScanLogger.warning("SqliScanConsumer ThreadPool more than 30, now: {scaningnum}".format(scaningnum=self.scaning))
            time.sleep(3)

    def threadcallback(self, obj):
        print(obj.result())
        ScanLogger.warning("SqliScanConsumer task callback, now total scaning task: %s, scaned task: %s" % (self.scaning, self.scaned))
        self.scaning = self.scaning - 1
        self.scaned = self.scaned + 1



def SqliScanMain():
    engine = create_engine('mysql+pymysql://root:123456@127.0.0.1:3306/test', pool_size=20, pool_recycle=599, pool_timeout=30)
    DB_Session = sessionmaker(bind=engine)
    sqli = SqliScanConsumer('amqp://guest:guest@localhost:5672/%2F', 'sqliscan', 'sqliscan.key', DB_Session)
    try:
        sqli.run()
    except KeyboardInterrupt:
        sqli.stop()


def main():
    # http://43.247.91.228:81/vulnerabilities/sqli/?id=1&Submit=Submit#
    req = RequestData()
    req.saveid = 1
    req.scanid = 2
    req.ct = ''
    req.scheme = 'http'
    req.netloc = '43.247.91.228:81'
    req.method = 'GET'
    req.path = '/vulnerabilities/sqli/'
    req.cookie = 'PHPSESSID=vophvn0qp2am6m5h22l1tiev56; security=low'
    req.ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    req.getData = {'id': '1', 'Submit': 'Submit'}
    req.postData = ''
    req.reqHeaders = {'Cookie': 'PHPSESSID=vophvn0qp2am6m5h22l1tiev56; security=low', 'Accept-Language': 'zh-CN,zh;q=0.9', 'Accept-Encoding': 'gzip, deflate', 'Referer': 'http://43.247.91.228:81/vulnerabilities/sqli/', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8', 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36', 'Upgrade-Insecure-Requests': '1'}
    sqliscanObj = SqliScan(req, 'a')
    sqliscanObj.run()


if __name__ == '__main__':
    main()
