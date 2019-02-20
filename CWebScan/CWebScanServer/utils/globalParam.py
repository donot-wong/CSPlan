#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-02-18 14:27:14
# @Author  : donot (donot@donot.me)
# @Link    : https://blog.donot.me

import logging

CONTENT_TYPE = ['application/x-www-form-urlencoded', 'multipart/form-data', 'application/json', 'text/xml']

ScanLogger = logging.getLogger('CWebScanServer')

# 黑名单参数名
BlackParamName = ['q', '_csrf']