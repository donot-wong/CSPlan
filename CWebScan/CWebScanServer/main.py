#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-02-19 15:30:05
# @Author  : donot (donot@donot.me)
# @Link    : https://blog.donot.me

from flask import Flask
from flask import request
from flask import json

app = Flask(__name__)

# 初始化
from lib.init import init


@app.route('/Receive', methods = ['POST'])
def ReceiveBody():
    # InitId = request.args.get('InitId')
    # requestId = request.args.get('requestId')
    from lib.rabbitqueue.initqueue import SourceDataQueue

    SourceDataQueue.basic_publish(exchange='', routing_key='dataprehandlequeue', body=request.get_data())

    return 'Ok'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='4579')