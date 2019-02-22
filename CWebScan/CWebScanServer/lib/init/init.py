#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-02-18 14:27:14
# @Author  : donot (donot@donot.me)
# @Link    : https://blog.donot.me

import multiprocessing
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
from lib.sourceparse.main import parseMain
from lib.scandistribution.distribute import distributeMain
from utils.globalParam import ScanLogger, CWebScanSetting
## 服务端环境初始化


## 数据库
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
engine = create_engine('mysql+pymysql://root:123456@127.0.0.1:3306/test')
DB_Session = sessionmaker(bind=engine)
CWebScanSetting.MysqlSession = DB_Session()

# 日志
import logging


loghandler = logging.FileHandler('scan.log', encoding='utf-8')
loghandler.setLevel(logging.DEBUG)
logging_format = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
loghandler.setFormatter(logging_format)
ScanLogger.addHandler(loghandler)


# 消费者子进程
p = multiprocessing.Process(target=parseMain)
p.daemon = False
p.start()


# 任务分发子进程
p = multiprocessing.Process(target=distributeMain)
p.daemon = False
p.start()


# sqlinject扫描子进程
# p = multiprocessing.Process(target=)
# p.daemon = False
# p.start()