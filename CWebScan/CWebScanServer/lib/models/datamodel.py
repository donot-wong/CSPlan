#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-02-22 11:14:58
# @Author  : donot (donot@donot.me)
# @Link    : https://blog.donot.me

from sqlalchemy import Column
from sqlalchemy.types import CHAR, Integer, String, Time, Text
from sqlalchemy.ext.declarative import declarative_base
import sys
import os
BaseModel = declarative_base()

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
from utils.globalParam import CWebScanSetting


def init_db():
    BaseModel.metadata.create_all(CWebScanSetting.engine)

def drop_db():
    BaseModel.metadata.drop_all(CWebScanSetting.engine)


class User(BaseModel):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(CHAR(100)) # or Column(String(30))


class data_raw(BaseModel):
	"""原始数据"""
	__tablename__ = 'data_raw'

	id = Column(Integer, primary_key=True)
	saveid = Column(String(100), unique=True)
	url = Column(String(255))
	method = Column(String(10))
	body = Column(Text(2000))
	# ua = Column(String(200))
	# cookie = Column(String(2000))
	reqheaders = Column(Text(2000))
	resheaders = Column(Text(1000))
	time = Column(Time)


class data_clean(BaseModel):
	"""清洗后数据"""
	__tablename__ = 'data_clean'

	id = Column(Integer, primary_key=True)
	saveid = Column(String(100), unique=True)
	netloc = Column(String(100))
	scheme = Column(String(10))
	method = Column(String(10))
	path = Column(String(255))
	query = Column(String(255))
	body = Column(Text(5000))
	ua = Column(String(200))
	cookie = Column(String(2000))
	reqheaders = Column(Text(2000))
	resheaders = Column(Text(1000))
	time = Column(Time)


class ScanTask(BaseModel):
	"""扫描任务"""
	id = Column(Integer, primary_key=True)
	dataid = Column(Integer)
	scantype = Column(Integer)
	time = Column(Time)
	status = Column(Integer) # 任务状态


class VulnData(BaseModel):
	"""漏洞报告"""
	id = Column(Integer, primary_key=True)
	dataid = Column(Integer)
	scanid = Column(Integer)
	vulntype = Column(Integer)
	time = Column(Time)
	status = Column(Integer )
