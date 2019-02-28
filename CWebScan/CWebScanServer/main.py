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

app = Flask(__name__)

# 初始化
from lib.init import init
credentials = pika.PlainCredentials('guest', 'guest')
parameters =  pika.ConnectionParameters('localhost', credentials=credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()
channel.exchange_declare(exchange="message", exchange_type="topic")


@app.route('/Receive', methods = ['POST'])
def ReceiveBody():
    try:
        channel.basic_publish('message', 'parsesrcdata.source', pickle.dumps(request.get_data()), pika.BasicProperties(content_type='text/plain', delivery_mode=1))
    except Exception as e:
        print(e)
        print(request.get_data())
    return 'Ok'


if __name__ == '__main__':
    # app.run(host='0.0.0.0', port='4579')
    data = b'{"InitId":"100011","requestId":"39012","url":"https://hangouts.google.com/_/scs/talk-static/_/js/k=wcs.inmolecalling.zh_CN.zYSdXi-Xs6E.O/am=C1A/rt=j/d=0/rs=AGyH-FuRgl1t7z1uWpdrHr7o72xrobgQbQ/m=syj,syk,dlh","method":"GET","initiator":"https://hangouts.google.com","bodyType":"empty","reqHeaders":{"Cookie":"HSID=AVI2vhwzrl6OgN3n0; SSID=AreaGCB0xCrL5qMXI; APISID=9KipWBXx23KXOdlv/ADBfzqjYMNBLZQujU; SAPISID=d7Cj349ruUSoTGMi/AmxDtYK_wjdSZHZQX; CONSENT=YES+CN.zh-CN+20180121-08-0; SID=7wa5AEMz-n3qlZEtjnd2HsbzT_ir1ibwJCupYpiDcX0GkIsWlpx2HkTruAkruizn0vMoSQ.; ANID=AHWqTUke5tIPRx2STgIKQkPIc9STv6KMLdIEDMVzM6fhSvrRk3RLWbNcKXZqbQST; OGPC=19010758-2:; OGP=-19010758:; NID=166=HLb2Ye9pFoCNs2FfYSm8h_upP0tb7u8xFefdT26ClX2aF3dBwXojgx8ruy24DME22KEHRRasI68VdWe9sCBTCOnGSMqnDrPwBqflvlrw6BcrYk0_FpRv9nVNlBEEx9Os-mqdJggQ2E7Pux90iT1o0-o8MIcdeSw6ghL0n8gAooOVFiPRo_SpshWM22cTkXvfQ7xltdL53dLF8-3WMHUScdo5CtKm3wdfItMCwne28M-OnQProiv1cw5n8mvvcyI; 1P_JAR=2019-02-27-15; SIDCC=AN0-TYshc91Xxxvsnr2_mnS9Kz12TMt0ojwo5iztJ663-7n6mz6VwGhSD_fDFA9U850jDbe0FiQ","Accept-Language":"zh-CN,zh;q=0.9","Accept-Encoding":"gzip, deflate, br","Referer":"https://hangouts.google.com/hangouts/_/hscv?pvt=AMP3uWa8kzgEMA57IYlgCcqBF8MfmnoMiOIaKPQPWcDH2PH1J77JO3ETfAXWG_Kz6ZMpvnCQq2-CztErMn-1iadMqLFFq9iqzg%3D%3D&authuser=0&xpc=%7B%22cn%22%3A%22XtA1MyuDbz%22%2C%22ppu%22%3A%22https%3A%2F%2Fmail.google.com%2Frobots.txt%22%2C%22lpu%22%3A%22https%3A%2F%2Fhangouts.google.com%2Frobots.txt%22%7D","X-Client-Data":"CJe2yQEIprbJAQjEtskBCKmdygEIqKPKAQixp8oBCL+nygEI4qjKAQjpqcoBGPmlygE=","Accept":"*/*","User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36"},"resIp":"127.0.0.1","statusCode":200,"resHeaders":{"status":"200","accept-ranges":"bytes","vary":"Accept-Encoding","content-encoding":"gzip","content-type":"text/javascript; charset=UTF-8","content-length":"7043","date":"Mon, 25 Feb 2019 21:48:34 GMT","expires":"Tue, 25 Feb 2020 21:48:34 GMT","last-modified":"Wed, 20 Feb 2019 22:18:25 GMT","x-content-type-options":"nosniff","server":"sffe","x-xss-protection":"1; mode=block","cache-control":"public, max-age=31536000","age":"59558","alt-svc":"quic=\\":443\\"; ma=2592000; v=\\"44,43,39\\""}}'
    channel.basic_publish('message', 'parsesrcdata.source', pickle.dumps(data), pika.BasicProperties(content_type='text/plain', delivery_mode=1))
    
