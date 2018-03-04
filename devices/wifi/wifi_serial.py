#!/usr/bin/python
# -*- coding: utf-8 -*-
#filename:wifi_serial.py
# model:6288
# usage：
'''
'''
import serial
import binascii
import time
logger = logging.getLogger('pos.log') 

class WIFI():
	baud_rate = 115200
    device_name = ''
    timeout = 0.3
    ser = None
    #馒头科技的at指令集
    ATcmd= { '测试AT启动':'AT',
             '重启模块':'AT+RST',
             '查看版本信息':'AT+GMR',

             '选择WIFI应用模式':'AT+CWMODE',
             '加入AP':'AT+CWJAP?',
             '列出当前可以AP':'AT+CWLAP',
             '退出与AP的连接':'AT+CWQAP',
             '设置AP模式下的参数':'AT+CWSAP',
             '查看已接入设备的IP':'AT+CWLIF',

             '获得连接状态':'AT+CIPSTATUS',
             '建立 TCP 连接或注册 UDP 端口号':'AT+CIPSTART',
             '发送数据':'AT+CIPSEND',
             '关闭 TCP 或 UDP':'AT+CIPCLOSE',
             '获取本地 IP 地址':'AT+CIFSR',
             '启动多连接':'AT+CIPMUX',
             '配置为服务器':'AT+CIPSERVER',
             '设置模块传输模式':'AT+CIPMODE',
             '设置服务器超时时间':'AT+CIPSTO',
             '网络固件升级':'AT+CIUPDATE',
             '接收到网络数据':'+IPD'
            }
	@staticmethod
    def opencom(device_name):
        try:
            WIFI.ser = serial.Serial(device_name,WIFI.baud_rate,timeout = WIFI.timeout)
            if WIFI.ser.isOpen():  
                if WIFI.get_version():
                    WIFI.device_name = device_name
                    logger.info('open right com:' + WIFI.device_name)
                    return True
                else:
                    return False
            else:
                return False
        except Exception, e:
            return False

    @staticmethod
    def com_detect():
        try:
            if WIFI.ser.isOpen():
                return True
        except Exception, e:
            if WIFI.opencom('/dev/ttyUSB0') == False:
                if WIFI.opencom('/dev/ttyUSB1') == False:
                    if WIFI.opencom('/dev/ttyUSB2') == False:
                        if WIFI.opencom('COM2') == False:
                            logger.error('open com failed')
                            return False
            return True

    @staticmethod
    def com_comfirm(cmd = 'AT'):
        WIFI.ser.write(cmd)
        rcvbuff = WIFI.ser.read(10)
        if rcvbuff == 'OK':
            return True
        else:
            return False 

    @staticmethod
    def cmd_process(cmd,parameter=''):
        cmd = ble.ATcmd[cmd]
        if parameter != '':
            if parameter == '?':
                cmd = cmd + parameter
            else:
                cmd = cmd + '['+ parameter + ']'
        print 'cmd:',cmd

        ble.ser.write(cmd)
        rcvbuff = ble.ser.read(200)
        if rcvbuff[:3] == 'OK+':
            print rcvbuff[3:]
            return rcvbuff[3:]
        elif rcvbuff == 'ERR+AT':
            print '指令错误'
            return False
        elif rcvbuff == 'ERR+PARA':
            print '参数错误'
            return False
        else:
            print 'data error:' + rcvbuff
            return False