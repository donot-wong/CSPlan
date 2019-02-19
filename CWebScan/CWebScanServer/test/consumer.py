#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-02-19 10:22:51
# @Author  : donot (donot@donot.me)
# @Link    : https://blog.donot.me

import pika
import pickle
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from utils.DataStructure import RequestData

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue="toscanqueue")

def callback(ch, method, properties, body):
	print(pickle.loads(body))


channel.basic_consume(callback, queue='toscanqueue', no_ack=True)

print("[*] Waiting for message. To exit press CTRL+C")

channel.start_consuming()

