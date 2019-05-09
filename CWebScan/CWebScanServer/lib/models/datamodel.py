#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-02-22 11:14:58
# @Author  : donot (donot@donot.me)
# @Link    : https://blog.donot.me

from sqlalchemy import Column, func
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
	chrometype = Column(String(5))
	url = Column(Text(1000))
	method = Column(String(10))
	body = Column(Text(5000))
	# ua = Column(String(200))
	# cookie = Column(String(2000))
	reqheaders = Column(Text(5000))
	resheaders = Column(Text(5000))
	parsestatus = Column(Integer)
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
	cookie = Column(Text(5000))
	reqheaders = Column(Text(5000))
	resheaders = Column(Text(5000))
	statuscode = Column(Integer)
	time = Column(DateTime, default=datetime.datetime.now)

class data_clean_key(BaseModel):
	"""去重key"""
	__tablename__ = 'data_clean_key'
	id = Column(Integer, primary_key=True)
	dataid = Column(Integer)
	keytype = Column(Integer)
	key1 = Column(String(32))
	key2 = Column(String(32))
	key3 = Column(String(100))
	key4 = Column(Integer)
	key5 = Column(String(32))


class ScanTask(BaseModel):
	"""扫描任务"""
	__tablename__ = 'scantask'
	id = Column(Integer, primary_key=True)
	dataid = Column(String(100)) # unique
	netloc = Column(String(100))
	scantype = Column(Integer)
	status = Column(Integer) # 任务状态
	createtime = Column(DateTime, server_default=func.now(), comment='创建时间')
	updatetime = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='修改时间')

class HostScan(BaseModel):
	"""主机扫描"""
	__tablename__ = 'hostscan'
	id = Column(Integer, primary_key=True)
	host = Column(String(100))


class VulnData(BaseModel):
	"""漏洞报告"""
	__tablename__ = 'vulndata'
	id = Column(Integer, primary_key=True)
	dataid = Column(String(100))
	scanid = Column(Integer)
	netloc = Column(String(100))
	vulntype = Column(Integer)
	time = Column(DateTime, default=datetime.datetime.now)
	status = Column(Integer)
	paramname = Column(String(100))
