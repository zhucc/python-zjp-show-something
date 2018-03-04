#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2016-05-17 14:24:52
# @Author  : zhuhua (you@example.org)
# @Module  : compro.py
# @Version : $Id$
#管理打印机和读卡器串口
from msprintdriver import printdevice
from multifunction_reader import reader
import ConfigParser
cf = ConfigParser.ConfigParser()
class comprocess:

	@staticmethod
	def savecom(dev_name,com_name):
		cf.read('showsys.conf')
		cf.set("device",dev_name, com_name)
		file = open("showsys.conf", "w")
		cf.write(file)
		file.close()

	@staticmethod
	def allocatecom():
		#get printer com
		#result = printdevice.com_detect()
		result = '/dev/ttyUSB0'
		if result:
			comprocess.savecom('printer',result)
		else:
			comprocess.savecom('printer','??')
			print 'find printer com failed'
		#get multifunction reader com
		#result = reader.com_detect()
		result = '/dev/ttyUSB1'
		if result:
			comprocess.savecom('reader',result)
		else:
			comprocess.savecom('reader','??')
			print 'find reader com failed'

	
if __name__ == '__main__':
	comprocess.allocatecom()







