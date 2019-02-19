#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-02-18 10:05:47
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))


# 数据源队列
SourceDataQueue = connection.channel()
SourceDataQueue.queue_declare(queue="dataprehandlequeue")


# 原始数据处理后需要进入扫描的数据队列
ToScanQueue = connection.channel()
ToScanQueue.queue_declare(queue='toscanqueue')


# 扫描队列
# 扫描类型队列后期可以从数据库读取配置后再进行架子啊
# 一期 直接通过代码写死
SqliScanQueue = connection.channel()
SqliScanQueue.queue_declare(queue='sqliscan')

RceScanQueue = connection.channel()
RceScanQueue.queue_declare(queue='rcescan')

JsonpScanQueue = connection.channel()
JsonpScanQueue.queue_declare(queue='jsonpscan')


# 扫描结果队列
ScanResultQueue = connection.channel()
ScanResultQueue.queue_declare(queue='scanresult')
