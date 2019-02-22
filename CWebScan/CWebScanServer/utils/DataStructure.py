#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-02-18 19:40:27
# @Author  : donot (donot@donot.me)
# @Link    : https://blog.donot.me
import copy
import types

# Request 数据格式
class RequestData(object):
	"""http 请求数据格式对象"""
	host = None
	method = None
	path = None
	contentType = None
	contentLength = None
	body = None
	otherHeader = {}

	def __init__(self):
		# self.arg = arg
		pass

	def __setattr__(self, key, value):
		self.__dict__[key] = value

	def __getattr__(self, key):
		return object.__getattribute__(self, key)

	# def __repr__(self):
	# 	return " method: " + self.method + ' statuscode: ' + self.statuscode


class AttribDict(dict):
    """
    This class defines the sqlmap object, inheriting from Python data
    type dictionary.

    >>> foo = AttribDict()
    >>> foo.bar = 1
    >>> foo.bar
    1
    """

    def __init__(self, indict=None, attribute=None):
        if indict is None:
            indict = {}

        # Set any attributes here - before initialisation
        # these remain as normal attributes
        self.attribute = attribute
        dict.__init__(self, indict)
        self.__initialised = True

        # After initialisation, setting attributes
        # is the same as setting an item

    def __getattr__(self, item):
        """
        Maps values to attributes
        Only called if there *is NOT* an attribute with this name
        """

        try:
            return self.__getitem__(item)
        except KeyError:
            raise AttributeError("unable to access item '%s'" % item)

    def __setattr__(self, item, value):
        """
        Maps attributes to values
        Only if we are initialised
        """

        # This test allows attributes to be set in the __init__ method
        if "_AttribDict__initialised" not in self.__dict__:
            return dict.__setattr__(self, item, value)

        # Any normal attributes are handled normally
        elif item in self.__dict__:
            dict.__setattr__(self, item, value)

        else:
            self.__setitem__(item, value)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, dict):
        self.__dict__ = dict

    def __deepcopy__(self, memo):
        retVal = self.__class__()
        memo[id(self)] = retVal

        for attr in dir(self):
            if not attr.startswith('_'):
                value = getattr(self, attr)
                if not isinstance(value, (types.BuiltinFunctionType, types.FunctionType, types.MethodType)):
                    setattr(retVal, attr, copy.deepcopy(value, memo))

        for key, value in self.items():
            retVal.__setitem__(key, copy.deepcopy(value, memo))

        return retVal


		
if __name__ == '__main__':
	test = RequestData()
	test.xxx = '127.0.0.1'
	print(test.xxx)
