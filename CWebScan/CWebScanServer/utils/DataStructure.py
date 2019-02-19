#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-02-18 19:40:27
# @Author  : donot (donot@donot.me)
# @Link    : https://blog.donot.me

# Request 数据格式
class RequestData(object):
	"""http 请求数据格式对象"""
	host = None
	method = None
	path = None
	contentType = None
	contentLength = None
	body = None
	otherHeader = {}

	def __init__(self):
		# self.arg = arg
		pass

	def __setattr__(self, key, value):
		self.__dict__[key] = value

	def __getattr__(self, key):
		return object.__getattribute__(self, key)

	def __repr__(self):
		return "url: " + self.url + " method: " + self.method + ' statuscode: ' + self.statuscode
		
		
if __name__ == '__main__':
	test = RequestData()
	test.xxx = '127.0.0.1'
	print(test.xxx)