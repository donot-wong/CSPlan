#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-02-18 14:27:14
# @Author  : donot (donot@donot.me)
# @Link    : https://blog.donot.me

from .DataStructure import AttribDict
import logging

CONTENT_TYPE = ['application/x-www-form-urlencoded', 'multipart/form-data', 'application/json', 'text/xml']

ScanLogger = logging.getLogger('CWebScanServer')

# 黑名单参数名
BlackParamName = ['q', '_csrf']

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

SqliVulnAlertTemplate = "SQL Inject({type}) Vuln Find! VulnId: {vulnid}, ScanId: {scanid}, Url: {url}, Method: {method}, Paramname: {paramname}, details please click url: {detailUrl}"
RceVulnAlertTemplate = "Rce{type} Vuln Find! ScanId: {scanid}, Url: {url}, Method: {method}, Paramname: {paramname}, details please click url: {detailUrl}"
ScanTaskErrorAlertTemplate = "ScanTask Error Alert! ScanId: {scanid}, ScanType: {scantype}, StartTime: {starttime}, ErrorInfo: {errorinfo}, MSG: {msg}"