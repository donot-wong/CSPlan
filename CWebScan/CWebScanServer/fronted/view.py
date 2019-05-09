#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-05-09 12:49:33
# @Author  : donot (donot@donot.me)
# @Link    : https://blog.donot.me

from flask_admin.contrib.sqla import ModelView

class RawDataView(ModelView):
	def get_query(self):
		self.session.flush()
		self.session.commit()
		return super(RawDataView, self).get_query()
	can_edit = False
	column_list = ('id', 'saveid', 'url', 'method', 'time')
	# column_searchable_list = ['name', 'email']
	column_searchable_list = ['saveid', 'url']
	column_labels = dict(saveid='统一标识', url='请求url', method='请求方法', time='添加时间')

class CleanDataView(ModelView):
	def get_query(self):
		self.session.flush()
		self.session.commit()
		return super(CleanDataView, self).get_query()
	can_edit = False
	column_list = ('id', 'saveid', 'scheme', 'netloc', 'method', 'path', 'statuscode', 'time')
	column_searchable_list = ['saveid', 'netloc']
	column_labels = dict(saveid='统一标识', scheme='协议', netloc='域名/IP', method='请求方法', path='请求路径', statuscode='响应状态码', time='添加时间')

class ScanTaskView(ModelView):
	def get_query(self):
		self.session.flush()
		self.session.commit()
		return super(ScanTaskView, self).get_query()
	can_edit = True
	column_searchable_list = ['id', 'netloc']
	column_labels = dict(id='id',dataid='关联数据ID', netloc='所属域名', scantype='扫描类型', status='扫描状态', createtime='任务创建时间', updatetime='任务更新时间')

class VulnDataView(ModelView):
	def get_query(self):
		self.session.flush()
		self.session.commit()
		return super(VulnDataView, self).get_query()
	can_edit = True
	column_searchable_list = ['scanid', 'netloc']
	column_labels = dict(id='id',dataid='关联数据ID', netloc='所属域名', scanid='扫描任务ID', vulntype='漏洞类型', status='漏洞状态', paramname='参数名称', time='创建时间')
