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

# 初始化
from lib.init import init
from lib.rabbitqueue.producerBase import PublisherBase

QueueReceive2ParseMain = multiprocessing.Queue()


def trans2parseMain(q):
    example = PublisherBase('amqp://guest:guest@localhost:5672/%2F?connection_attempts=3&heartbeat_interval=3600', 'parsesrcdata', 'parsesrcdata.source', q)
    example.run()


@app.route('/Receive', methods = ['POST'])
def ReceiveBody():
    QueueReceive2ParseMain.put(pickle.dumps(request.get_data()))
    return 'Ok'


if __name__ == '__main__':
    p = multiprocessing.Process(target=trans2parseMain, args=(QueueReceive2ParseMain,))
    p.daemon = False
    p.start()
    app.run(host='0.0.0.0', port='4579')
