#!/usr/bin/python
# -*- coding: utf-8 -*-
#filename:scanner.py; model:honeywell 3310g
import serial
import binascii
class scanner():
        #串口设置
        device_name = "/dev/ttyUSB0"
        baud_rate = 115200
        timeout = 1
        ser = None
        
    @staticmethod
    def opencom(device_name):
        try:
            scanner.ser = serial.Serial(device_name,scanner.baud_rate,timeout = scanner.timeout)
            if scanner.ser.isOpen():
                if scanner.getversion():
                    scanner.device_name = device_name
                    logger.info('open right com:' + scanner.device_name)
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
            if reader.ser.isOpen():
                return True
        except Exception, e:
            if scanner.opencom('/dev/ttyUSB0') == False:
                if scanner.opencom('/dev/ttyUSB1') == False:
                    if scanner.opencom('/dev/ttyUSB2') == False:
                        if scanner.opencom('/dev/ttyUSB3') == False:
                            return False
            return True
        
    @staticmethod 
    #返回条码或者二维码的字符串   
    def rcvdata():
        datarcv = scan_gun.ser.readline()
        datarcv = binascii.b2a_hex(datarcv)
        return datarcv

if __name__=='__main__':
    scan_gun.openSerial("/dev/ttyUSB0",115200)
    while(1):
        a = scan_gun.rcvdata()
        if a:
            print a
