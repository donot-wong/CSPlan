#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-02-22 11:14:58
# @Author  : donot (donot@donot.me)
# @Link    : https://blog.donot.me

from sqlalchemy import Column
from sqlalchemy.types import CHAR, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
import datetime
import sys
import os
BaseModel = declarative_base()

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
from utils.globalParam import CWebScanSetting


def init_db():
    BaseModel.metadata.create_all(CWebScanSetting.engine)

def drop_db():
    BaseModel.metadata.drop_all(CWebScanSetting.engine)


class data_raw(BaseModel):
	"""原始数据"""
	__tablename__ = 'data_raw'

	id = Column(Integer, primary_key=True)
	saveid = Column(String(100))
	url = Column(Text(1000))
	method = Column(String(10))
	body = Column(Text(5000))
	# ua = Column(String(200))
	# cookie = Column(String(2000))
	reqheaders = Column(Text(5000))
	resheaders = Column(Text(5000))
	time = Column(DateTime, default=datetime.datetime.now)


class data_clean(BaseModel):
	"""清洗后数据"""
	__tablename__ = 'data_clean'

	id = Column(Integer, primary_key=True)
	saveid = Column(String(100))
	netloc = Column(String(100))
	scheme = Column(String(10))
	method = Column(String(10))
	path = Column(Text(1000))
	query = Column(Text(1000))
	body = Column(Text(5000))
	# ua = Column(String(200))
	ct = Column(String(200))
	cookie = Column(String(5000))
	reqheaders = Column(Text(5000))
	resheaders = Column(Text(5000))
	statuscode = Column(Integer)
	time = Column(DateTime, default=datetime.datetime.now)


class ScanTask(BaseModel):
	"""扫描任务"""
	__tablename__ = 'scantask'
	id = Column(Integer, primary_key=True)
	dataid = Column(String(100)) # unique
	scantype = Column(Integer)
	time = Column(DateTime, default=datetime.datetime.now)
	status = Column(Integer) # 任务状态


class VulnData(BaseModel):
	"""漏洞报告"""
	__tablename__ = 'vulndata'
	id = Column(Integer, primary_key=True)
	dataid = Column(String(100))
	scanid = Column(Integer)
	vulntype = Column(Integer)
	time = Column(DateTime, default=datetime.datetime.now)
	status = Column(Integer)
