#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-03-05 11:46:52
# @Author  : donot (donot@donot.me)
# @Link    : https://blog.donot.me

import requests
SlackHookUrl = "https://hooks.slack.com/services/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"

def send2slack(msg):
	payload = {"text": msg}
	header = {'Content-Type': 'application/json'}
	res = requests.post(SlackHookUrl, data=str(payload), headers=header)
	if res.text == 'ok':
		return True, res.text
	else:
		return False, res.text


def main():
	restatus, msg = send2slack('Scantask finished! Scanid: 12345, url: http://baidu.com, status:1, result: no find!')
	if restatus:
		print('ok')
	else:
		print('failed')

if __name__ == '__main__':
	main()