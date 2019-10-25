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
from utils.globalParam import CWebScanSetting, ScanLogger,  BlackParamName, BLACK_COOKIE_KEY_LIST, BLACK_HTTP_HEADER_KEY_LIST, ScanTaskStatus, VulnType, AlertTemplateDict, CalcAverageTimeLimitCnt
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

        # referer cookie header注入扫描
        self.headerScan()

        self.changeScanStatus()

    def headerScan(self):
        if len(self.cookie) > 0:
            for key in self.cookieDict:
                if key != 'other':
                    flag = False
                    for black_cookie_key in BLACK_COOKIE_KEY_LIST:
                        if black_cookie_key.lower() in key:
                            flag = True
                            break
                    if flag:
                        continue
                    else:
                        if self.errorbased('header-cookie', key):
                            self.saveScanResult(VulnType['sqli-error'], 'Cookie: ' + key)
                        elif self.timebased('header-cookie', key):
                            self.saveScanResult(VulnType['sqli-time'], 'Cookie: ' + key)
                        else:
                            continue
                else:
                    continue
        else:
            pass

        if 'Referer' in self.SrcRequestHeaders:
            if self.errorbased('header', 'Referer'):
                self.saveScanResult(VulnType['sqli-error'], 'Referer')
            elif self.timebased('header', 'Referer'):
                self.saveScanResult(VulnType['sqli-time'], 'Referer')
            else:
                pass
        if 'User-Agent' in self.SrcRequestHeaders:
            if self.errorbased('header', 'User-Agent'):
                self.saveScanResult(VulnType['sqli-error'], 'User-Agent')
            elif self.timebased('header', 'User-Agent'):
                self.saveScanResult(VulnType['sqli-time'], 'User-Agent')
            else:
                pass

        # other header
        for header_key in self.SrcRequestHeaders:
            if header_key.lower() in BLACK_HTTP_HEADER_KEY_LIST:
                pass
            else:
                if self.errorbased('header', header_key):
                    self.saveScanResult(VulnType['sqli-error'], 'Header: ' + header_key)
                elif self.timebased('header', header_key):
                    self.saveScanResult(VulnType['sqli-time'], 'Header: ' + header_key)
                else:
                    pass


    def errorbased(self, loc, key):
        '''
        基于报错的注入扫描
        '''
        if loc == 'params':
            _getData = copy.copy(self.getData)
            for error_payload in SQLiPayload_ErrorBased:
                _getData[key] = str(self.getData[key]) + error_payload
                res = self.reqSend(loc, _getData, self.url, self.method, self.cookie, self.ua, self.ct, self.SrcRequestHeaders)
                self.sendreqCnt += 1
                if self.checkIsErrorBaseSqli(res):
                    return True
        elif loc == 'data' and self.dataformat == 'FORMDATA':
            _postData = copy.copy(self.postData)
            for error_payload in SQLiPayload_ErrorBased:
                _postData[key] = str(self.postData[key]) + error_payload
                res = self.reqSend(loc, _postData, self.url, self.method, self.cookie, self.ua, self.ct, self.SrcRequestHeaders)
                self.sendreqCnt += 1
                if self.checkIsErrorBaseSqli(res):
                    return True
        elif loc == 'data' and self.dataformat == 'JSON':
            _postData = copy.copy(self.jsondata)
            for error_payload in SQLiPayload_ErrorBased:
                _postData[key] = str(self.jsondata[key]) + error_payload
                res = self.reqSend(loc, json.dumps(_postData), self.url, self.method, self.cookie, self.ua, self.ct, self.SrcRequestHeaders)
                self.sendreqCnt += 1
                if self.checkIsErrorBaseSqli(res):
                    return True
        elif loc == 'header-cookie':
            _cookie = copy.copy(self.cookieDict)
            _header = copy.copy(self.SrcRequestHeaders)
            for error_payload in SQLiPayload_ErrorBased:
                _cookie[key] = self.cookieDict[key] + error_payload
                _header['Cookie'] = self.cookieDict2Str(_cookie)
                res = self.reqSend('header', header=_header, cookie={})
                self.sendreqCnt += 1
                if self.checkIsErrorBaseSqli(res):
                    return True
        elif loc == 'header':
            _header = copy.copy(self.SrcRequestHeaders)
            for error_payload in SQLiPayload_ErrorBased:
                _header[key] = self.SrcRequestHeaders[key] + error_payload
                res = self.reqSend('header', header=_header)
                self.sendreqCnt += 1
                if self.checkIsErrorBaseSqli(res):
                    return True
        else:
            ScanLogger.warning('Can not handle this request\'s method: %s' % self.method)
            return False
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
            _getData = copy.copy(self.getData)
            for payload_idx in range(len(SQLiPayload_Sleep)):
                _getData[key] = str(self.getData[key]) + SQLiPayload_Sleep[payload_idx].format(sleep='sleep(2)')
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
        elif loc== 'data' and self.dataformat == 'FORMDATA':
            _postData = copy.copy(self.postData)
            for payload_idx in range(len(SQLiPayload_Sleep)):
                _postData[key] = str(self.postData[key]) + SQLiPayload_Sleep[payload_idx].format(sleep='sleep(2)')
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
        elif loc == 'data' and self.dataformat == 'JSON':
            _postData = copy.copy(self.jsondata)
            for payload_idx in range(len(SQLiPayload_Sleep)):
                _postData[key] = str(self.jsondata[key]) + SQLiPayload_Sleep[payload_idx].format(sleep='sleep(2)')
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
        elif loc == 'header-cookie':
            _cookie = copy.copy(self.cookieDict)
            _header = copy.copy(self.SrcRequestHeaders)
            for payload_idx in range(len(SQLiPayload_Sleep)):
                _cookie[key] = self.cookieDict[key] + SQLiPayload_Sleep[payload_idx].format(sleep='sleep(2)')
                _header['Cookie'] = self.cookieDict2Str(_cookie)
                res = self.reqSend('header', header=_header, cookie={})
                self.sendreqCnt += 1
                if res is None:
                    continue
                if res.elapsed.total_seconds() > max(MIN_VALID_DELAYED_RESPONSE, self.delayTimeJudgeStandard):
                    if self.twiceCheckForTimeBased(loc, key, payload_idx, res.elapsed.total_seconds()):
                        return True
                    else:
                        return False
                else:
                    continue
        elif loc == 'header':
            _header = copy.copy(self.SrcRequestHeaders)
            for payload_idx in range(len(SQLiPayload_Sleep)):
                _header[key] = self.SrcRequestHeaders[key] + SQLiPayload_Sleep[payload_idx].format(sleep='sleep(2)')
                res = self.reqSend('header', header=_header)
                self.sendreqCnt += 1
                if res is None:
                    continue
                if res.elapsed.total_seconds() > max(MIN_VALID_DELAYED_RESPONSE, self.delayTimeJudgeStandard):
                    if self.twiceCheckForTimeBased(loc, key, payload_idx, res.elapsed.total_seconds()):
                        return True
                    else:
                        return False
                else:
                    continue
        else:
            ScanLogger.warning('Can not handle this request\'s method: %s' % self.method)
            return False
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
                _getData[key] = str(self.getData[key]) + SQLiPayload_Sleep_Normal[payload_idx]
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
            elif loc == 'data' and self.dataformat == 'FORMDATA':
                _postData = copy.copy(self.postData)
                _postData[key] = str(self.postData[key]) + SQLiPayload_Sleep_Normal[payload_idx]
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
            elif loc == 'data' and self.dataformat == 'JSON':
                _postData = copy.copy(self.jsondata)
                _postData[key] = str(self.jsondata[key]) + SQLiPayload_Sleep_Normal[payload_idx]
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
            elif loc == 'header-cookie':
                _cookie = copy.copy(self.cookieDict)
                _header = copy.copy(self.SrcRequestHeaders)
                _cookie[key] = self.cookieDict[key] + SQLiPayload_Sleep_Normal[payload_idx]
                _header['Cookie'] = self.cookieDict2Str(_cookie)
                res = self.reqSend('header', header=_header, cookie={})
                self.sendreqCnt += 1
                if res.elapsed.total_seconds() < max(MIN_VALID_DELAYED_RESPONSE, self.delayTimeJudgeStandard):
                    _cookie[key] = self.cookieDict[key] + SQLiPayload_Sleep[payload_idx].format(sleep='sleep(2)')
                    _header['Cookie'] = self.cookieDict2Str(_cookie)
                    res = self.reqSend('header', header=_header, cookie={})
                    self.sendreqCnt += 1
                    if res.elapsed.total_seconds() >= max(MIN_VALID_DELAYED_RESPONSE, self.delayTimeJudgeStandard):
                        return True
                    else:
                        return False
                else:
                    return False
            elif loc == 'header':
                _header = copy.copy(self.SrcRequestHeaders)
                _header[key] = self.SrcRequestHeaders[key] + SQLiPayload_Sleep_Normal[payload_idx]
                res = self.reqSend(loc, header=_header)
                if res.elapsed.total_seconds() < max(MIN_VALID_DELAYED_RESPONSE, self.delayTimeJudgeStandard):
                    _header[key] = self.SrcRequestHeaders[key] + SQLiPayload_Sleep[payload_idx].format(sleep='sleep(2)')
                    res = self.reqSend(loc, header=_header)
                    if res.elapsed.total_seconds() >= max(MIN_VALID_DELAYED_RESPONSE, self.delayTimeJudgeStandard):
                        return True
                    else:
                        return False
                else:
                    return False
            else:
                return False
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
        if len(self.respTimeList) == 0:
            # min_resp_time = 0
            self.delayTimeJudgeStandard = 0
        else:
            # min_resp_time = min(self.respTimeList)
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


    def on_message(self, _unused_channel, basic_deliver, properties, body):
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
    engine = create_engine(CWebScanSetting.MYSQL_URL, pool_size=20, pool_recycle=599, pool_timeout=30)
    DB_Session = sessionmaker(bind=engine)
    sqli = SqliScanConsumer(CWebScanSetting.AMQP_URL, 'sqliscan', 'sqliscan.key', DB_Session)
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
