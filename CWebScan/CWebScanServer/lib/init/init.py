#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-02-18 14:27:14
# @Author  : donot (donot@donot.me)
# @Link    : https://blog.donot.me

import multiprocessing
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
from lib.sourceparse.parsedata import parseMain, trans2distribute
from lib.scandistribution.distribute import distributeMain, distributeTrans
from lib.scanscript.sqliScan import SqliScanMain
from lib.scanscript.rceScan import RceScanMain
# from lib.scanscript.filescan import FileScanMain
from utils.globalParam import ScanLogger, CWebScanSetting
## 服务端环境初始化


## 数据库
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine(CWebScanSetting.MYSQL_URL, pool_size=20, pool_recycle=599, pool_timeout=30)
DB_Session = sessionmaker(bind=engine)
CWebScanSetting.DB_Session = DB_Session
CWebScanSetting.engine = engine

from lib.models.datamodel import init_db, drop_db
drop_db()
init_db()

# 日志
import logging


loghandler = logging.FileHandler('scan.log', encoding='utf-8')
loghandler.setLevel(logging.DEBUG)
logging_format = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
loghandler.setFormatter(logging_format)
ScanLogger.addHandler(loghandler)



########################################################################################################################
# 源数据解析子进程
parseMainTransQueue = multiprocessing.Queue()
p = multiprocessing.Process(target=parseMain, args=(parseMainTransQueue,))
p.daemon = False
p.start()

# 源数据解析结果分发子进程
p = multiprocessing.Process(target=trans2distribute, args=(parseMainTransQueue,))
p.daemon = False
p.start()
########################################################################################################################





########################################################################################################################
# 任务调度处理子进程
distributeTransQueue = multiprocessing.Queue()
p = multiprocessing.Process(target=distributeMain, args=(distributeTransQueue,))
p.daemon = False
p.start()

# 分发任务调度结果
p = multiprocessing.Process(target=distributeTrans, args=(distributeTransQueue,))
p.daemon = False
p.start()
# 任务分发处理子进程
########################################################################################################################



# sqlinject扫描子进程
p = multiprocessing.Process(target=SqliScanMain)
p.daemon = False
p.start()


# rce扫描子进程
p = multiprocessing.Process(target=RceScanMain)
p.daemon = False
p.start()


# file扫描子进程
# p = multiprocessing.Process(target=FileScanMain) 
# p.daemon = False
# p.start()