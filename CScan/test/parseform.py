#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-12-05 19:37:14
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$
from parseheader import parse_options_header


class MultiPartParser(object):

	_empty_string_iter = repeat('')

	def __init__(self, data, charset='utf-8'):
		# super(MultiPartParser, self).__init__()
		self.data = data
		self.charset = charset

    def _find_terminator(self, iterator):
        """The terminator might have some additional newlines before it.
        There is at least one application that sends additional newlines
        before headers (the python setuptools package).
        """
        for line in iterator:
            if not line:
                break
            line = line.strip()
            if line:
                return line
        return b''

	def parse_lines(self, data, boundary, content_length):
        next_part = b'--' + boundary
        last_part = next_part + b'--'

        iterator = chain(make_line_iter(data), self._empty_string_iter)

        terminator = self._find_terminator(iterator)

        if terminator == last_part:
        	return
        elif terminator != next_part:
        	return

        while terminator != last_part:
        	headers = parse_multipart_headers(iterator)


if __name__ == '__main__':
	main()