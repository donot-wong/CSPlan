#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-02-19 15:30:05
# @Author  : donot (donot@donot.me)
# @Link    : https://blog.donot.me
import pickle
import pika
import sys
import json
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
from lib.rabbitqueue.consumerBase import ConsumerBase
from utils.DataStructure import RequestData
from utils.globalParam import ScanLogger


class DistributeConsumer(ConsumerBase):
    def __init__(self, ampq_url, queue_name, routing_key):
        super(DistributeConsumer, self).__init__(ampq_url, queue_name, routing_key)

    def on_message(self, unused_channel, basic_deliver, properties, body):
        data = pickle.loads(body)
        ScanLogger.warning('DistributeConsumer received message # %s from %s: %s',
                    basic_deliver.delivery_tag, properties.app_id, data.netloc)
        self.acknowledge_message(basic_deliver.delivery_tag)


def distributeMain():
    example = DistributeConsumer('amqp://guest:guest@localhost:5672/%2F', 'distribute', 'distribute.source')
    try:
        example.run()
    except KeyboardInterrupt:
        example.stop()
