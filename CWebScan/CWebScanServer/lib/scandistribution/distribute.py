#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-02-19 15:30:05
# @Author  : donot (donot@donot.me)
# @Link    : https://blog.donot.me
import pickle
import pika
import sys
import os

def distributeMain():
	connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
	channel = connection.channel()

	channel.queue_declare(queue="toscanqueue")

	def callback(ch, method, properties, body):
		reqData = pickle.loads(body)
		

	channel.basic_consume(callback, queue='toscanqueue', no_ack=True)
	channel.start_consuming()
