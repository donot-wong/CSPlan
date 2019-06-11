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
from urllib import parse
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
from utils.DataStructure import RequestData
from utils.globalParam import ScanLogger
from utils.globalParam import XML_RECOGNITION_REGEX
from utils.globalParam import JSON_RECOGNITION_REGEX
from utils.globalParam import JSON_LIKE_RECOGNITION_REGEX
from utils.globalParam import MULTIPART_RECOGNITION_REGEX
from multipart import FormParser
from io import BytesIO

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
    normal_field = {}
    file_field = {}
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
            self.ret.dataformat = 'FORMDATA'
            res = self._parseFormData()
            reqbody = dict()
            for key in res:
                reqbody[key] = res[key][0]
                # reqbody.append(key + "=" + res[key][0])
            self.ret.postData = reqbody
        elif self.chormeType == 'raw':
            res = self._parseRawData()
            self.ret.postData = res
        else:
            # self.ret.postData = self.data
            res = self._parseRawData()
            self.ret.postData = res

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
        self.ret.getData = dict([(k,v[0]) for k,v in getParemDicts.items()])


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
        self.parseCT()
        self.parseUrl()
        self.ret.postData = ''
        if self.chormeType in ['formData', 'raw']:
            self.parseData()
        else:
            self.ret.dataformat = 'NOBODY'
            if self.ret.query == '':
                self.ret.dataformat = 'ALLNO'
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
        _data = self.data
        _data_raw = parse.unquote(_data)
        sts, data = self.dataFormatIdent(_data_raw)
        return data


    def dataFormatIdent(self, data):
        # print(data)
        if re.search(JSON_RECOGNITION_REGEX, data):
            # return True, 'JSON', json.loads(data)
            self.ret.dataformat = 'JSON'
            # return True, json.loads(data)
            return True, data
        elif re.search(JSON_LIKE_RECOGNITION_REGEX, data):
            self.ret.dataformat = 'UNKNOWN'
            return False, data
        elif re.search(XML_RECOGNITION_REGEX, data):
            self.ret.dataformat = 'XML'
            return True, data
        elif re.search(MULTIPART_RECOGNITION_REGEX, data):
            self.ret.dataformat = 'MULTIPART'
            self.parseMulti(data)
            if len(self.normal_field) > 0:
                self.ret.multi_normal_fields = self.normal_field
            else:
                self.ret.multi_normal_fields = {}
            if len(self.file_field) > 0:
                self.ret.multi_file_fields = self.file_field
            else:
                self.ret.multi_file_fields = {}
            return True, data
        else:
            self.ret.dataformat = 'UNKNOWN'
            return False, data

    def on_field(self, field):
        # print("Parsed field named: %s:%s" % (field.field_name,field.value))
        self.normal_field[str(field.field_name, encoding='utf-8')] = str(field.value, encoding='utf-8')
        # print(field)

    def on_file(self, file):
        # print("Parsed file named: %s:%s" % (file.field_name,file.file_name))
        self.file_field[str(file.field_name, encoding='utf-8')] = str(file.file_name, encoding='utf-8')


    def parseMulti(self, data):
        formParserObj = FormParser(
            self.ret.contentType,
            self.on_field,
            self.on_file,
            boundary=self.ret.boundary
        )
        formParserObj.write(bytes(data, encoding = "utf8"))
        formParserObj.finalize()

    def __repr__(self):
        return "chromeType: " + self.chormeType + " contentType: " + self.contentType + " data: " + self.data[:100]


if __name__ == '__main__':
    parseTest = ParseBase('https://passport.baidu.com/sys/preview/36b9e9bb94e7ac9b7238', 'raw', 'multipart/form-data; boundary=----WebKitFormBoundaryAwaS9VBdpfkdbDjR', '{\"0\":\"------WebKitFormBoundaryAwaS9VBdpfkdbDjR%0D%0AContent-Disposition%3A+form-data%3B+name%3D%22bdstoken%22%0D%0A%0D%0A6a622c8ac38ccfeb94ece5c94a4bb3fb%0D%0A------WebKitFormBoundaryAwaS9VBdpfkdbDjR%0D%0AContent-Disposition%3A+form-data%3B+name%3D%22psign%22%0D%0A%0D%0A36b9e9bb94e7ac9b7238%0D%0A------WebKitFormBoundaryAwaS9VBdpfkdbDjR%0D%0AContent-Disposition%3A+form-data%3B+name%3D%22staticpage%22%0D%0A%0D%0Ahttps%3A//www.baidu.com/p/jump.html%0D%0A------WebKitFormBoundaryAwaS9VBdpfkdbDjR%0D%0AContent-Disposition%3A+form-data%3B+name%3D%22file%22%3B+filename%3D%221.png%22%0D%0AContent-Type%3A+image/png%0D%0A%0D%0A\",\"1\":\"C%3A%5CUsers%5Cdonot-windows%5CPictures%5C1.png\",\"2\":\"%0D%0A------WebKitFormBoundaryAwaS9VBdpfkdbDjR--%0D%0A\"}')
    res = parseTest.parse()
    # print((res.getData))
    # parseTest.parse()
    # print(res.dataformat)
    # print(urlparse('http://baidu.com/search/1'))
