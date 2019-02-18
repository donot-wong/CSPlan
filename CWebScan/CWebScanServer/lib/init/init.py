#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-02-18 14:27:14
# @Author  : donot (donot@donot.me)
# @Link    : https://blog.donot.me


## 服务端环境初始化


# 日志
# import logging


# loghandler = logging.FileHandler('flask.log', encoding='utf-8')
# loghandler.setLevel(logging.DEBUG)
# logging_format = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
# loghandler.setFormatter(logging_format)
# app.logger.addHandler(loghandler)

# 消费者
import multiprocessing
import sys
sys.path.append('../../')
from sourceparse.main import mainConsumer
p = multiprocessing.Process(target=mainConsumer)
p.daemon = False
p.start()