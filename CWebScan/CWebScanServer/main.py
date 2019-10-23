#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-02-19 15:30:05
# @Author  : donot (donot@donot.me)
# @Link    : https://blog.donot.me

from flask import Flask
from flask import request
from flask import json
import pickle
import pika
import multiprocessing

app = Flask(__name__)
app.config['SECRET_KEY'] = "donot123!@#"

# 初始化
from lib.init import init
from lib.rabbitqueue.producerBase import PublisherBase

trans2parseMainQueue = multiprocessing.Queue()
# from flask_admin import Admin
# from flask_admin.contrib.sqla import ModelView
# from fronted.view import RawDataView,CleanDataView,ScanTaskView,VulnDataView,ConfigView
from lib.models.datamodel import data_raw, data_clean, ScanTask, VulnData, Config
from utils.globalParam import CWebScanSetting
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(CWebScanSetting.MYSQL_URL, pool_size=20, pool_recycle=599, pool_timeout=30)
dbsession = sessionmaker(bind=engine)
# admin = Admin(app, name='后台管理系统', template_mode='bootstrap3')
# admin.add_view(RawDataView(data_raw, dbsession(), name="原始数据"))
# admin.add_view(CleanDataView(data_clean, dbsession(), name="清洗后数据"))
# admin.add_view(ScanTaskView(ScanTask, dbsession(), name="扫描任务"))
# admin.add_view(VulnDataView(VulnData, dbsession(), name="漏洞发现"))
# admin.add_view(ConfigView(Config, dbsession(), name='系统配置'))

def trans2parseMain(q):
    example = PublisherBase(CWebScanSetting.AMQP_URL + "&heartbeat=0", 'parsesrcdata', 'parsesrcdata.source', q)
    example.run()


@app.route('/Receive', methods = ['POST'])
def ReceiveBody():
    # trans2parseMainQueue.put(pickle.dumps(request.get_data()))
    return 'Ok'


if __name__ == '__main__':
    # p = multiprocessing.Process(target=trans2parseMain, args=(trans2parseMainQueue,))
    # p.daemon = False
    # p.start()
    # trans2parseMainQueue.put(pickle.dumps('{"InitId":"816983","requestId":"210251","url":"https://console.cloud.tencent.com/cgi/message?action=getMsgSummary&t=1551432955251&uin=755234308&ownerUin=0&csrfCode=1626631735&regionId=4","method":"GET","initiator":"https://console.cloud.tencent.com","bodyType":"empty","reqHeaders":{"Cookie":"language=zh; _ga=GA1.2.1270828730.1547791557; pgv_pvi=6942151680; qcloud_uid=06fe25fc442f00d393d6360c1b36ea7a; lastLoginType=wx; _gcl_au=1.1.1770649078.1547791560; pgv_pvid=1105071061; qcmainCSRFToken=SJP_tUtQUV; qcloud_visitId=a43355736673662e1fb528b497963b16; pgv_si=s8033893376; wss_xsrf=2f2b4be0aaf7a23e92c87e6e8f0c3673%7C1551238790; loginType=wx; nodesess=2a0bd8ea-bc1c-fd67-9e52-17e87b45586d; appid=1251754651; moduleId=1251754651; opc_xsrf=703903fb9fab8ba12b4adb3ad481bf61%7C1551238819; pgv_info=ssid=s1217110844; qcloud_from=qcloud.google.seo-1551259253676; uin=o755234308; tinyid=144115200792168817; intl=1; regionId=4; qcact.sid=s%3Al6x-wqEKgUUTJ7YYn6C4xq-nMhaqGgPV.gmA190eWcW7PBcXB2Qs0mFw2kiQD%2BVXZW%2FQfas7V2oc; skey=r1aKg*rn*JdvInFAnwq9A06ekKujhfN62KT4AKeR8q4_; nick=%E5%82%BB%E5%82%BB%E5%82%BB%E5%82%BB%E5%AD%90; systemTimeGap=1779; ownerUin=O755234308G","Accept-Language":"zh-CN,zh;q=0.9","Accept-Encoding":"gzip, deflate, br","Referer":"https://console.cloud.tencent.com/cvm/eip","User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36","X-Requested-With":"XMLHttpRequest","Accept":"application/json, text/javascript, */*; q=0.01"},"resIp":"119.29.48.127","statusCode":200,"resHeaders":{"status":"200","server":"nginx","date":"Fri, 01 Mar 2019 09:35:57 GMT","content-type":"text/plain;charset=utf-8","content-length":"185","x-powered-by":"Express","x-req-id":"rJr-T_LIN"}}'))
    app.run(host='0.0.0.0', port='4579')
