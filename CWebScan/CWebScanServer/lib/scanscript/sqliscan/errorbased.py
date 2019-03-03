#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-02-20 17:02:28
# @Author  : donot (donot@donot.me)
# @Link    : https://blog.donot.me
import requests

plainArray = [
	'Microsoft OLE DB Provider for ODBC Drivers',
    'Error Executing Database Query',            
	'Microsoft OLE DB Provider for SQL Server',
	'ODBC Microsoft Access Driver',
	'ODBC SQL Server Driver',
	'supplied argument is not a valid MySQL result',
	'You have an error in your SQL syntax',
	'Incorrect column name',
	'Syntax error or access violation:',
    'Invalid column name',
    'Must declare the scalar variable',
    'Unknown system variable',
    'unrecognized token: ',
	'undefined alias:',
	'Can\'t find record in',
	'2147217900',
	'Unknown table',
	'Incorrect column specifier for column',
	'Column count doesn\'t match value count at row',
	'Unclosed quotation mark before the character string',
	'Unclosed quotation mark',
	'Call to a member function row_array() on a non-object in',
	'Invalid SQL:',
	'ERROR: parser: parse error at or near',
	'): encountered SQLException [',
	'Unexpected end of command in statement [',
	'[ODBC Informix driver][Informix]',
	'[Microsoft][ODBC Microsoft Access 97 Driver]',
	'Incorrect syntax near ',
	'[SQL Server Driver][SQL Server]Line 1: Incorrect syntax near',
	'SQL command not properly ended',
	'unexpected end of SQL command',
	'Supplied argument is not a valid PostgreSQL result',
	'internal error [IBM][CLI Driver][DB2/6000]',
    'PostgreSQL query failed',    
    'Supplied argument is not a valid PostgreSQL result',
	'pg_fetch_row() expects parameter 1 to be resource, boolean given in',
    'unterminated quoted string at or near',
    'unterminated quoted identifier at or near',
    'syntax error at end of input',
    'Syntax error in string in query expression',
    'Error: 221 Invalid formula',
	'java.sql.SQLSyntaxErrorException',
    'SQLite3::query(): Unable to prepare statement:',
	'<title>Conversion failed when converting the varchar value \'A\' to data type int.</title>',
	'SQLSTATE=42603',
	'org.hibernate.exception.SQLGrammarException:',
	'org.hibernate.QueryException',
	'System.Data.SqlClient.SqlException:',	
	'SqlException',
	'SQLite3::SQLException:',
    'Syntax error or access violation:',
    'Unclosed quotation mark after the character string',
    'You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near',
	'PDOStatement::execute(): SQLSTATE[42601]: Syntax error:',
    '<b>SQL error: </b> no such column',
    '附近有语法错误',
    '后的引号不完整'
]
regexArray = [
	r"/(Incorrect\ssyntax\snear\s'[^']*')/",
	r"/(Syntax error: Missing operand after '[^']*' operator)/",
	r"/Syntax error near\s.*?\sin the full-text search condition\s/",
	r'/column "\w{5}" does not exist/',
	r"/near\s[^:]+?:\ssyntax\serror/",
	r"/(pg_query\(\)[:]*\squery\sfailed:\serror:\s)/",
	r"/('[^']*'\sis\snull\sor\snot\san\sobject)/",
	r"/(ORA-\d{4,5}:\s)/",
	r"/(Microsoft\sJET\sDatabase\sEngine\s\([^\)]*\)<br>Syntax\serror(.*)\sin\squery\sexpression\s'.*\.<br><b>.*,\sline\s\d+<\/b><br>)/",
	r"/(<h2>\s<i>Syntax\serror\s(\([^\)]*\))?(in\sstring)?\sin\squery\sexpression\s'[^\.]*\.<\/i>\s<\/h2><\/span>)/",
	r"/(<font\sface=\"Arial\"\ssize=2>Syntax\serror\s(.*)?in\squery\sexpression\s'(.*)\.<\/font>)/",
	r"/(<b>Warning<\/b>:\s\spg_exec\(\)\s\[\<a\shref='function.pg\-exec\'\>function\.pg-exec\<\/a>\]\:\sQuery failed:\sERROR:\s\ssyntax error at or near \&quot\;\\\&quot; at character \d+ in\s<b>.*<\/b>)/",
	r"/(System\.Data\.OleDb\.OleDbException\:\sSyntax\serror\s\([^)]*?\)\sin\squery\sexpression\s.*)/",
	r"/(System\.Data\.OleDb\.OleDbException\:\sSyntax\serror\sin\sstring\sin\squery\sexpression\s)/",
	r"/(Data type mismatch in criteria expression|Could not update; currently locked by user '.*?' on machine '.*?')/",
	r'/(<font style="COLOR: black; FONT: 8pt\/11pt verdana">\s+(\[Macromedia\]\[SQLServer\sJDBC\sDriver\]\[SQLServer\]|Syntax\serror\sin\sstring\sin\squery\sexpression\s))/',
	r"/(Unclosed\squotation\smark\safter\sthe\scharacter\sstring\s'[^']*')/",
	r"/((<b>)?Warning(<\/b>)?:\s+(?:mysql_fetch_array|mysql_fetch_row|mysql_fetch_object|mysql_fetch_field|mysql_fetch_lengths|mysql_num_rows)\(\): supplied argument is not a valid MySQL result resource in (<b>)?.*?(<\/b>)? on line (<b>)?\d+(<\/b>)?)/",
	r"/((<b>)?Warning(<\/b>)?:\s+(?:mysql_fetch_array|mysql_fetch_row|mysql_fetch_object|mysql_fetch_field|mysql_fetch_lengths|mysql_num_rows)\(\) expects parameter \d+ to be resource, \w+ given in (<b>)?.*?(<\/b>)? on line (<b>)?\d+(<\/b>)?)/",
	r"/(You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near '[^']*' at line \d)/",
	r'/(Query\sfailed\:\sERROR\:\scolumn\s"[^"]*"\sdoes\snot\sexist\sLINE\s\d)/',
	r"/(Query\sfailed\:\sERROR\:\s+unterminated quoted string at or near)/",
	r"/(The string constant beginning with .*? does not have an ending string delimiter\.)/",
	r"/(Unknown column '[^']+' in '\w+ clause')/",
]


def test():
	res = requests.get('http://43.247.91.228:81/vulnerabilities/sqli/?id=1&Submit=Submit#')
	print(res.text)
	for i in plainArray:
		if i in res.text:
			print('yes')

if __name__ == '__main__':
	test()
