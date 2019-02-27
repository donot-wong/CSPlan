#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-02-18 14:27:14
# @Author  : donot (donot@donot.me)
# @Link    : https://blog.donot.me

import json
import re
from urllib.parse import unquote_to_bytes as _unquote
from urllib.parse import parse_qs
from urllib.parse import urlparse
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
from utils.DataStructure import RequestData
from utils.globalParam import ScanLogger


_option_header_start_mime_type = re.compile(r',\s*([^;,\s]+)([;,]\s*.+)?')

_option_header_piece_re = re.compile(r'''
    ;\s*
    (?P<key>
        "[^"\\]*(?:\\.[^"\\]*)*"  # quoted string
    |
        [^\s;,=*]+  # token
    )
    \s*
    (?:  # optionally followed by =value
        (?:  # equals sign, possibly with encoding
            \*\s*=\s*  # * indicates extended notation
            (?P<encoding>[^\s]+?)
            '(?P<language>[^\s]*?)'
        |
            =\s*  # basic notation
        )
        (?P<value>
            "[^"\\]*(?:\\.[^"\\]*)*"  # quoted string
        |
            [^;,]+  # token
        )?
    )?
    \s*
''', flags=re.VERBOSE)


class ParseBase(object):
	CONTENT_TYPE = ['application/x-www-form-urlencoded', 'multipart/form-data', 'application/json', 'text/xml']
	chormeType = None
	contentType = None
	data = None
	url = None
	ret = None
	def __init__(self, url, chormeType, contentType, data):
		self.chormeType = chormeType
		self.contentType = contentType
		self.data = data
		self.url = url
		self.ret = RequestData()

	def parseData(self):
		'''
		解析post参数
		'''
		self.ret.chromeType = self.chormeType
		if self.chormeType == 'formData':
			res = self._parseFormData()
			reqbody = {}
			for key in res:
				reqbody[key] = res[key]
				# reqbody.append(key + "=" + res[key][0])
			self.ret.postData = reqbody

		elif self.chormeType == 'raw':
			res = self._parseRawData()
			self.ret.postData = self.data
		else:
			self.ret.postData = self.data

	def parseUrl(self):
		'''
		解析get参数
		'''
		o = urlparse(self.url)
		self.ret.scheme = o.scheme
		self.ret.netloc = o.netloc
		self.ret.path = o.path
		self.ret.query = o.query
		getParemDicts = parse_qs(o.query, keep_blank_values=True)
		self.ret.getData = getParemDicts


	def parseCT(self):
		'''
		解析ContentType
		'''
		res = self._parse_options_header(self.contentType)
		if len(res) == 1:
			self.ret.contentType = res[0]
		elif len(res) == 2:
			self.ret.contentType = res[0]
			if 'charset' in res[1]:
				self.ret.charset = res[1]['charset']
			elif 'boundary' in res[1]:
				self.ret.boundary = res[1]['boundary']
			else:
				pass
		else:
			ScanLogger.info('Parse ContentType Failed, ContentType: ' + self.contentType)

	def parse(self):
		if self.chormeType != 'empty':
			self.parseData()
		self.parseCT()
		self.parseUrl()
		return self.ret

	def _unquote_header_value(self, value, is_filename=False):
	    if value and value[0] == value[-1] == '"':
	        value = value[1:-1]
	        if not is_filename or value[:2] != '\\\\':
	            return value.replace('\\\\', '\\').replace('\\"', '"')
	    return value

	def _parse_options_header(self, value, multiple=False):
	    if not value:
	        return '', {}

	    result = []

	    value = "," + value.replace("\n", ",")
	    while value:
	        match = _option_header_start_mime_type.match(value)
	        if not match:
	            break
	        result.append(match.group(1))  # mimetype
	        options = {}
	        # Parse options
	        rest = match.group(2)
	        while rest:
	            optmatch = _option_header_piece_re.match(rest)
	            if not optmatch:
	                break
	            option, encoding, _, option_value = optmatch.groups()
	            option = self._unquote_header_value(option)
	            if option_value is not None:
	                option_value = self._unquote_header_value(
	                    option_value,
	                    option == 'filename')
	                if encoding is not None:
	                    option_value = _unquote(option_value).decode(encoding)
	            options[option] = option_value
	            rest = rest[optmatch.end():]
	        result.append(options)
	        if multiple is False:
	            return tuple(result)
	        value = rest

	    return tuple(result) if result else ('', {})

	def _parseFormData(self):
		return json.loads(self.data)

	def _parseRawData(self):
		return None


	def __repr__(self):
		return "chromeType: " + self.chormeType + " contentType: " + self.contentType + " data: " + self.data[:100]


if __name__ == '__main__':
	parseTest = ParseBase('http://baidu.com/search/1?id=1&name=2', 'formData', 'application/x-www-form-urlencoded; charset=UTF-8', "{\"metadata[]\":[\"\"],\"path\":[\"%2FROOT%2FHOME\"]}")
	res = parseTest.parse()
	print(res.__dict__)
	# parseTest.parse()
