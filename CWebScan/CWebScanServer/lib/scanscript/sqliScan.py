#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-02-20 17:02:28
# @Author  : donot (donot@donot.me)
# @Link    : https://blog.donot.me

import pickle
import pika
import sys
import os
import requests


class SqliScanBase(object):
    """docstring for SqliScanBase"""
    SrcRequest = None
    def __init__(self, request):
        self.SrcRequest = request
    
    def run(self):
        '''
        线程中调用的函数
        '''
        pass

    def function():
        pass

