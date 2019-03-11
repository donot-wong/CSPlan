#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-02-18 14:27:14
# @Author  : donot (donot@donot.me)
# @Link    : https://blog.donot.me

from .DataStructure import AttribDict
import logging
import random

CONTENT_TYPE = ['application/x-www-form-urlencoded', 'multipart/form-data', 'application/json', 'text/xml']

ScanLogger = logging.getLogger('CWebScanServer')

# 黑名单参数名
BlackParamName = ['_t', '_csrf', 't', '_p', 'csrf', 'csrftoken', 'nonce', 'timestamp', 'submit', 'Submit', '']
IGNORE_PARAMETERS = ("__VIEWSTATE", "__VIEWSTATEENCRYPTED", "__VIEWSTATEGENERATOR", "__EVENTARGUMENT", "__EVENTTARGET", "__EVENTVALIDATION", "ASPSESSIONID", "ASP.NET_SESSIONID", "JSESSIONID", "CFID", "CFTOKEN")


CWebScanSetting = AttribDict()
CWebScanSetting.log_suffix = 'sqvds.cn'
CWebScanSetting.dnslog_prefix = 'xxx'
CWebScanSetting.weblog_prefix = 'xxx'
CWebScanSetting.dnslog_api = "http://admin.sqvds.cn" + '/api/' + '32d6e7038e8cb3c752364c9e1e69ff33790562b7' +  '/dnslog/' + '{searchstr}'
CWebScanSetting.weblog_api = "http://admin.sqvds.cn" + '/api/' + '32d6e7038e8cb3c752364c9e1e69ff33790562b7' +  '/weblog/' + '{searchstr}'

# Regular expression for XML POST data
XML_RECOGNITION_REGEX = r"(?s)\A\s*<[^>]+>(.+>)?\s*\Z"

# Regular expression used for detecting JSON POST data
JSON_RECOGNITION_REGEX = r'(?s)\A(\s*\[)*\s*\{.*"[^"]+"\s*:\s*("[^"]*"|\d+|true|false|null).*\}\s*(\]\s*)*\Z'

# Regular expression used for detecting JSON-like POST data
JSON_LIKE_RECOGNITION_REGEX = r"(?s)\A(\s*\[)*\s*\{.*'[^']+'\s*:\s*('[^']+'|\d+).*\}\s*(\]\s*)*\Z"

# Regular expression used for detecting multipart POST data
MULTIPART_RECOGNITION_REGEX = r"(?i)Content-Disposition:[^;]+;\s*name="

CalcAverageTimeLimitCnt = 13 # 计算请求平均时间最小发包量

# Coefficient used for a time-based query delay checking (must be >= 7)
TIME_STDEV_COEFF = 7

# Minimum response time that can be even considered as delayed (not a complete requirement)
MIN_VALID_DELAYED_RESPONSE = 0.5


ScanTaskVulnType = {
	'sqli': 1,
	'rce': 2,
	'xss': 3
}

ScanTaskStatus = {
	'running': 0,
	'completed': 1,
	'error': 2,
	'repeat_check_failed': 3,
	'rce_dnslog_send_finish_check_no': 4,
}

VulnType = {
	'sqli-error': 1,
	'sqli-boolean': 2,
	'sqli-time': 3,
	'rce-dnslog': 4,
	'rce-resp': 5,
	'rce-weblog': 6
}

AlertTemplateDict = {
	"0": "ScanTask Error Alert! ScanId: {scanid}, ScanType: {scantype}, StartTime: {starttime}, ErrorInfo: {errorinfo}, MSG: {msg}",
	"1": "SQL Inject(errorbased) Vuln Find! VulnId: {vulnid}, ScanId: {scanid}, Url: {url}, Method: {method}, Paramname: {paramname}, details please click url: {detailUrl}",
	"2": "SQL Inject(booleanbased) Vuln Find! VulnId: {vulnid}, ScanId: {scanid}, Url: {url}, Method: {method}, Paramname: {paramname}, details please click url: {detailUrl}",
	"3": "SQL Inject(timebased) Vuln Find! VulnId: {vulnid}, ScanId: {scanid}, Url: {url}, Method: {method}, Paramname: {paramname}, details please click url: {detailUrl}",
	"4": "Rce Vuln Find! ScanId: {scanid}, Url: {url}, Method: {method}, Paramname: {paramname}, details please click url: {detailUrl}"
}