#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-03-05 11:46:52
# @Author  : donot (donot@donot.me)
# @Link    : https://blog.donot.me

import requests
import string
import random

SlackHookUrl = "https://hooks.slack.com/services/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"

def send2slack(msg):
	payload = {"text": msg}
	header = {'Content-Type': 'application/json'}
	res = requests.post(SlackHookUrl, data=str(payload), headers=header)
	if res.text == 'ok':
		return True, res.text
	else:
		return False, res.text


def randomRange(start=0, stop=1000, seed=None):
    """
    Returns random integer value in given range

    >>> random.seed(0)
    >>> randomRange(1, 500)
    423
    """

    if seed is not None:
        random.seed(seed)
        randint = random.randint
    else:
        randint = random.randint

    return int(randint(start, stop))

def randomInt(length=4, seed=None):
    """
    Returns random integer value with provided number of digits

    >>> random.seed(0)
    >>> randomInt(6)
    874254
    """

    if seed is not None:
        random.seed(seed)
        choice = random.choice
    else:
        choice = random.choice

    return int("".join(choice(string.digits if _ != 0 else string.digits.replace('0', '')) for _ in range(0, length)))

def randomStr(length=4, lowercase=False, alphabet=None, seed=None):
    """
    Returns random string value with provided number of characters

    >>> random.seed(0)
    >>> randomStr(6)
    'RNvnAv'
    """

    if seed is not None:
        random.seed(seed)
        choice = random.choice
    else:
        choice = random.choice

    if alphabet:
        retVal = "".join(choice(alphabet) for _ in range(0, length))
    elif lowercase:
        retVal = "".join(choice(string.ascii_lowercase) for _ in range(0, length))
    else:
        retVal = "".join(choice(string.ascii_letters) for _ in range(0, length))

    return retVal


def main():
	restatus, msg = send2slack('Scantask finished! Scanid: 12345, url: http://baidu.com, status:1, result: no find!')
	if restatus:
		print('ok')
	else:
		print('failed')

if __name__ == '__main__':
	xlist = []
	for i in range(0,10000):
		_ = randomInt(7)
		if _ in xlist:
			print("boom")
			print(len(xlist))
			print(_)
			break
		xlist.append(_)
