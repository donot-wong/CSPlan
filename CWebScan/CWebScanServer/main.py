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
    channel.basic_publish('message', 'example.text', pickle.dumps(request.get_data()), pika.BasicProperties(content_type='text/plain', delivery_mode=1))

    return 'Ok'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='4579')
