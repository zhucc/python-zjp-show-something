#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
from functools import wraps
def fn_timer(function):
    @wraps(function)
    def function_timer(*args, **kwargs):
        t0 = time.time()
        result = function(*args, **kwargs)
        t1 = time.time()
        print ("Total time running %s: %s seconds" %
            (function.func_name, str(t1-t0)))
        return result
    return function_timer

class a():
	@staticmethod
	@fn_timer
	def change1(data):
		for i in range(100000):
			data = '55'
			bindata = bin(int(data,16))[2:]
			bindata = (bindata+'000')[-8:]
			data = format(int(bindata,2),'x')
		return data

	@staticmethod
	@fn_timer
	def change2(data):
		for i in range(100000):
			data = '55'
			data = int(data,16)<<3
			data = data&0xff
			data = format(data,'x')
		return data

if __name__ == '__main__':
	print a.change1('55')
	print a.change2('55')


