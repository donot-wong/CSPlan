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
BlackParamName = ['_t', '_csrf', 't', '_p', 'csrf', 'csrftoken', 'nonce', 'timestamp']

CWebScanSetting = AttribDict()

ScanTaskVulnType = {
	'sqli': 1,
	'rce': 2,
	'xss': 3
}

ScanTaskStatus = {
	'running': 0,
	'completed': 1,
	'error': 2
}

VulnType = {
	'sqli-error': 1,
	'sqli-boolean': 2,
	'sqli-time': 3,
	'rce': 4
}

AlertTemplateDict = {
	"0": "ScanTask Error Alert! ScanId: {scanid}, ScanType: {scantype}, StartTime: {starttime}, ErrorInfo: {errorinfo}, MSG: {msg}",
	"1": "SQL Inject(errorbased) Vuln Find! VulnId: {vulnid}, ScanId: {scanid}, Url: {url}, Method: {method}, Paramname: {paramname}, details please click url: {detailUrl}",
	"2": "SQL Inject(booleanbased) Vuln Find! VulnId: {vulnid}, ScanId: {scanid}, Url: {url}, Method: {method}, Paramname: {paramname}, details please click url: {detailUrl}",
	"3": "SQL Inject(timebased) Vuln Find! VulnId: {vulnid}, ScanId: {scanid}, Url: {url}, Method: {method}, Paramname: {paramname}, details please click url: {detailUrl}",
	"4": "Rce Vuln Find! ScanId: {scanid}, Url: {url}, Method: {method}, Paramname: {paramname}, details please click url: {detailUrl}"
}