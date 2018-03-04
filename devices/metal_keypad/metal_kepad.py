#!/usr/bin/env python
# -*- coding: utf-8 -*-
# filename:metal_keypad.py
# model：snk088a
# 函数请使用参考xz_f10指令集说明
import serial
import binascii
import re
import time
class keypad():
    baud_rate = 9600
    device_name = ''
    timeout = 0.1
    ser = None
    value2key={'31':'1','32':'2','33':'3','34':'4',
               '35':'5','36':'6','37':'7','38':'8',
               '39':'9','2e':'.','30':'0','08':'backup',
               '1b':'return','21':'up','22':'down','0d':'confirm'}
    
    @staticmethod
    def opencom(device_name):
        keypad.device_name = device_name
        try:
            keypad.ser = serial.Serial(keypad.device_name,keypad.baud_rate,timeout = keypad.timeout)
            if keypad.ser.isOpen():
                if keypad.getversion():
                    return True
                else:
                    return False
            else:
                return False
        except Exception, e:
            return False

    @staticmethod
    def com_detect():
        if keypad.opencom('/dev/ttyUSB0') == False:
            if keypad.opencom('/dev/ttyUSB1') == False:
                if keypad.opencom('/dev/ttyUSB2') == False:
                    if keypad.opencom('/dev/ttyUSB3') == False:
                        return False
        return True

    @staticmethod    
    #输入字符串后返回命令
    def splitcmd(str1):
        #get length
        n_len = len(str1)/2
        s_len = hex(n_len)
        s_len = s_len[2:]
        if n_len <16:
            s_len = '0'+s_len
            
        #get bcc   
        n_bcc = 0
        strlist = re.findall(r'(.{2})',str1)
        for i in strlist:
            n_bcc = n_bcc^int(i,16)
        n_bcc = n_bcc^n_len
        s_bcc = (hex(n_bcc))[2:]
        str1 = s_len+str1+s_bcc
        
        #make cmd  split
        strlist = re.findall(r'(.{1})',str1)
        s_splitcmd = '02'
        for i in strlist:
            i = int(i,16)
            if i > 9:
                s_splitcmd = s_splitcmd + str(i + 31)
            else:
                s_splitcmd = s_splitcmd + str(i + 30)
        s_splitcmd = s_splitcmd+'03'
        return s_splitcmd    
    
    @staticmethod
    def combinecmd(str1):
        if str1[-2:]=='03':
            str1 = str1[:-2]
        str1 = str1[2:]
        strlist = re.findall(r'(.{2})',str1)
        s_combinecmd = ''
        for i in strlist:
            num = int(i)
            if num < 40:
                i = hex(num - 30)[2:]
            else:
                i = hex(num - 31)[2:]
            s_combinecmd = s_combinecmd + i
        return s_combinecmd 
    
    @staticmethod
    def _sendcmd(cmddata):
        try:
            cmd = keypad.splitcmd(cmddata)
            keypad.ser.write(cmd.decode('hex'))
            datarcv = keypad.ser.readline()
            datarcv = binascii.b2a_hex(datarcv)
            datarcv = keypad.combinecmd(datarcv)
            return datarcv
        except Exception, e:
            return False
        

    @staticmethod
    #1.2 取产品版本号
    def getversion():
        datarcv = keypad._sendcmd('30')
        if datarcv:
            return datarcv
        else:
            return False

    @staticmethod
    #1.3 程序复位自检
    def reset():
        datarcv = keypad._sendcmd('31')
        if datarcv:
            if datarcv[2:4] == '04':
                return True
            else:
                return False
        else:
            return False

    @staticmethod
    #1.4 下装主密钥
    def loadmk(mainkeynumber,tmk):
        datarcv = keypad._sendcmd('32' + mainkeynumber + tmk)
        if datarcv:
            if datarcv[2:4] == '04':
                return True
            else:
                return False
        else:
            return False
        
    @staticmethod
    #1.5 下装工作密钥
    def loadwk(mainkeynumber,workkeynumber,workkey_encrypt):
        datarcv = keypad._sendcmd('33' + mainkeynumber + workkeynumber + workkey_encrypt)
        if datarcv:
            if datarcv[2:4] == '04':
                return True
            else:
                return False
        else:
            return False

    @staticmethod
    #1.6 设置账号
    def setaccount(card_number):
        newnumber = ''
        for i in range (len(card_number)):
            newnumber = newnumber + '3' + card_number[:1]
            card_number = card_number[1:]
        datarcv = keypad._sendcmd('34' + newnumber)
        if datarcv:
            if datarcv[2:4] == '04':
                return True
            else:
                return False
        else:
            return False        

    @staticmethod
    #1.7 启动密码键盘加密
    def open_encryptkeypad(pinlen = '06',disp = '01',jm_md = '00',ts_md = '00',timeout = '14') :
        datarcv = keypad._sendcmd('35' + pinlen + disp + jm_md + ts_md + timeout)
        if datarcv:
            if datarcv[2:4] == '04':
                return True
            else:
                return False
        else:
            return False
    
    @staticmethod
    #1.8 数据加密
    def data_encrypt(data):
        datarcv = keypad._sendcmd( '36' + data )
        if datarcv:
            if datarcv[2:4] == '04':
                return datarcv[4:-2]
            else:
                return False
        else:
            return False

    @staticmethod
    #1.9 数据解密
    def data_decode(data):
        datarcv = keypad._sendcmd( '37' + data )
        if datarcv:
            if datarcv[2:4] == '04':
                return datarcv[4:-2]
            else:
                return False
        else:
            return False

    @staticmethod
    #1.12 数据 MAC 运算
    def mac_encrypt(data):
        datarcv = keypad._sendcmd( '41' + data )
        if datarcv:
            if datarcv[2:4] == '04':
                return datarcv[4:-2]
            else:
                return False
        else:
            return False

    @staticmethod
    #1.13 取键盘中密码
    def get_encryptpin():
        datarcv = keypad._sendcmd('42')
        if datarcv:
            if datarcv[2:4] == '04':
                return datarcv[4:-2]
            else:
                return False
        else:
            return False
    
    @staticmethod
    #1.14 激活工作密钥
    def active_wk(mainkeynumber,workkeynumber):
        datarcv = keypad._sendcmd('43' + mainkeynumber + workkeynumber)
        if datarcv:
            if datarcv[2:4] == '04':
                return True
            else:
                return False
        else:
            return False

    @staticmethod
    #1.16 操作开关键盘和按键声音
    def operate_keypad(ctldata = '01'):
        datarcv = keypad._sendcmd('45' + ctldata)
        if datarcv:
            if datarcv[2:4] == '04':
                return True
            else:
                return False
        else:
            return False
    
    @staticmethod
    #1.17 算法处理参数
    def setparameter(pdata,fdata):
        datarcv = keypad._sendcmd('46' + pdata + fdata)
        if datarcv:
            if datarcv[2:4] == '04':
                return True
            else:
                return False
        else:
            return False


    @staticmethod    
    def rcvkeypad():
        try:
            datarcv = keypad.ser.readline()
            if datarcv:
                datarcv = binascii.b2a_hex(datarcv)
                keydata = ''
                num = len(datarcv)/2
                for i in range (num):
                    head = datarcv[:2]
                    if head in keypad.value2key:
                        keydata = keydata + keypad.value2key[head]
                        datarcv = datarcv[2:]
                    else:
                        return 'rcv error'
                return keydata
        except Exception, e:
            raise e
        
if __name__=='__main__':
    if keypad.com_detect():
        
        print keypad.getversion()
        print keypad.operate_keypad()
        print keypad.operate_keypad('00')
        print 'loadmk:',keypad.loadmk('00','01020304050607080900010203040506')
        print keypad.setparameter('00','30')
        print 'loadwk:',keypad.loadwk('00','00','10203040506070809000010203040506')
        
        
        # mac begin
        print 'active_wk:',keypad.active_wk('00','00')
        print keypad.setparameter('01','30')
        print keypad.setparameter('06','03')
        print 'mac:',keypad.mac_encrypt('3132333435363738')
        # mac end 
       
        
        print 'data_encrypt:',keypad.data_encrypt('3132333435363738')
        print 'data_decode:',keypad.data_decode('3132333435363738')

        #test pin encrypt
        print 'active_wk:',keypad.active_wk('00','00')
        print keypad.setparameter('02','00')
        print keypad.setparameter('01','20')
        print keypad.setparameter('05','01')
        print keypad.setparameter('04','10')
        print keypad.setaccount('990123456789')
        print keypad.operate_keypad('02')
        print 'open_encryptkeypad:',keypad.open_encryptkeypad()
        num = 0
        for i in range (100):
            data = keypad.ser.read(4)
            if data:
                num = num + 1
            if num == 6:
                break 
        print 'get_encryptpin:',keypad.get_encryptpin()
        #end of test pin encrypt
      
    else:
        print 'connect error'    
        



