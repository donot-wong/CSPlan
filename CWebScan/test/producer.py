#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-01-02 10:30:08
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))