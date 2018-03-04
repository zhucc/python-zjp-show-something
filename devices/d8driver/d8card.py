#!/usr/bin/python
#-*-coding:utf-8-*-
#filename:d8card.py

import sys
sys.path.append(sys.path[0][:-12])

import serial
import binascii

from src.tools.myLogger import Logger

"""
	D8卡操作类：
	   openSerial()   #打开串口
	   getCardNo(delaytime = 100)    #获取卡号,delaytime延迟多久去读卡,单位ms
	   serSerialRate(flag = 0)  #设置串口波特率，默认为0/9600bps
	   setBuzzer(time0 = 3, time1 = 0, times = 1)    #触发蜂鸣器，详见接口定义
"""

class CardHanle:
	machineName = "/dev/ttyUSB0"
	buadRate = 9600

	@staticmethod
	def dataFormat(data):
		"""
		:param data:
		:return: 拼接串口命令，成功返回拼接好的16进制字符窜命令，错误返回 -1
		"""
		data_start = "02"
		data_end = "03"
		length = len(data)/2
		if length > 9:
			Logger.info("数据太长，不支持!!!")
			return False
		data = data_start + "000" + str(length) + data
		checkNum = 0
		for i in range(2,len(data)+1,2):
			checkNum ^= int(data[i-2:i],16)
		all_data = data + CardHanle.myHex(checkNum) + data_end
		Logger.info("fomat data successful: {0}".format(all_data))
		return  all_data.decode("hex")

	@staticmethod
	def myHex(data):
		data = hex(data)[2:]
		if len(data) == 1:
			return "0" + data
		else:
			return data
	@staticmethod
	def openSerial():
		"""
		打开串口
		:return:成功返回串口句柄，失败返回False
		"""
		try:
			ser = serial.Serial(CardHanle.machineName,CardHanle.buadRate,timeout = 2)
			if ser.isOpen():
				Logger.info("serial open success")
				return ser
			else:
				Logger.error("serial open falied!!!!")
				return False
		except Exception,e:
			Logger.error("no serial line::{0}".format(e))
			return False

	@staticmethod
	def serSerialRate(flag = 0):
		"""
		:param flag: 串口通信波特率标记，
							0： 9600
							1： 19200
							2： 38400
							3： 57600
							4： 115200
		:return:成功返回True，失败返回 Flase
		"""
		cmd_flag = "C01000"
		cmd = cmd_flag + CardHanle.myHex(flag)
		send_data = CardHanle.dataFormat(cmd)
		ser = CardHanle.openSerial()
		if ser:
			ser.write(send_data)
			recvdata = ser.read(2)
			recvdata = binascii.b2a_hex(recvdata)
			if "02000200000003" == recvdata:
				return True
			else:
				return False
	@staticmethod
	def getCardNo(delaytime = 100, times = 1):
		"""
		:param delaytime:读卡延迟时间，单位ms，可选参数delaytime,默认100ms
		:times 读卡次数，默认为1
		:return:成功返回字符窜类型的卡号，失败返回 -1
		ps：默认尝试读卡10次，10次均读不到卡测判定读卡失败
		"""
		try:
			cmd_flag = "C140"
			data = CardHanle.myHex(delaytime/255) + CardHanle.myHex(delaytime%255)
			cmd = cmd_flag + data + "00"
			send_data = CardHanle.dataFormat(cmd)
			ser = CardHanle.openSerial()
			if ser:
				try:
					for i in range(times):
						ser.write(send_data)
						recvdata = ser.read(30)
						recvdata = binascii.b2a_hex(recvdata)
						cardNoLen = recvdata[12:14]
						cardNo = recvdata[14:-4]
						if int(cardNoLen,16) == len(cardNo)/2:
							arr = []
							for i in range(0,len(cardNo)+1,2):
								arr.append(cardNo[i:i+2])
							brr = ""
							for i in range(len(arr),0,-1):
								brr += str(arr[i-1])
							cardNo = int(brr,16)
							Logger.info("get cardNo successful ::{0}".format(cardNo))
							return cardNo
						else:
							Logger.error("dirty data!!")
					return -1
				except Exception,e:
					Logger.error("getCardNo error::{0}".format(e))
					return -1
			else:
				return -1
		except Exception,e:
			Logger.error("read card failed!!!::{0}".format(e))
			return -1
	@staticmethod
	def setBuzzer(time0 = 6, time1 = 0, times = 1):
		"""
		:param time0:蜂鸣器响的时间 单位100ms
		:param time1: 蜂鸣器鸣响间隔  单位100ms
		:param times: 蜂鸣器鸣响次数
		:return:True表示成功，False表示失败
		"""
		cmd_flag = "C013"
		cmd = cmd_flag + CardHanle.myHex(time0) + CardHanle.myHex(time1) + CardHanle.myHex(times)
		send_data = CardHanle.dataFormat(cmd)
		ser = CardHanle.openSerial()
		if ser:
			ser.write(send_data)
			recvdata = ser.read(7)
			recvdata = binascii.b2a_hex(recvdata)
			if "02000200000003" == recvdata:
				Logger.info("setBuzzer warning 1s successful")
				return True
			else:
				Logger.error("setBuzzer warning error!!!!!")
				return False
		else:
			return -1

if __name__ == "__main__":
	print CardHanle.getCardNo(0)
	CardHanle.setBuzzer()