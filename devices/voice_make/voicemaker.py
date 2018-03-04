#!/usr/bin/env python
# -*- coding: gbk -*-
#filename:voicemaker.py modle:syn6228
import serial
import binascii
import re
class voicedevice:
    baud_rate = 9600
    device_name = "/dev/ttyUSB0"
    timeout = 1
    ser = None
        
    @staticmethod
    def openSerial():
        voicedevice.ser = serial.Serial(voicedevice.device_name,voicedevice.baud_rate,timeout = voicedevice.timeout)
        try:
            if self.ser.isOpen():
                return self.ser
            else:
                return False
        except Exception,e:
            return -1
        
    #输入语音字符串后返回命令
    @staticmethod
    def getcmd(str1):
        str1 = binascii.hexlify(str1)
        cmd = 'fd'
        length = len(str1)/2+3
        strlen = hex(length)
        strlen = strlen[2:]
        if length <=15:
            strlen = '0' +strlen
        strlen = '00' +strlen
        cmd = cmd +strlen +'01'+'01'
        cmd = cmd +str1
        #print length +3 命令长度字节
        getcrc = 0 
        strlist = re.findall(r'(.{2})',cmd)
        for i in strlist:
            getcrc = getcrc^int(i,16)
        getcrc = (hex(getcrc))[2:]
        cmd =cmd + getcrc
        return cmd

    @staticmethod  
    def speakstring(string):
        if len(string) > 200:
            return 'string too long'
        else:
            cmd = voicedevice.getcmd(string)
            voicedevice.ser.write( cmd.decode('hex') )

    #文本数量太大时，先使用getcmd处理全部文本，再使用speakcmd
    @staticmethod
    def speakcmd(cmd):
        voicedevice.ser.write( cmd.decode('hex') )

    @staticmethod   
    def checkmodule():
        voicedevice.ser.write( 'FD000221DE'.decode('hex') )
        datarcv = voicedevice.ser.readline()
        datarcv = binascii.b2a_hex(datarcv)
        return datarcv

if __name__=='__main__':
    print voicedevice.openSerial() 
    print voicedevice.checkmodule()
    voicedevice.speakstring('你好')



