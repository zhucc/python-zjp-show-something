#!/usr/bin/env python
# -*- coding: utf-8 -*-
# filename:metal_keypad.py
# model：snk088a
# 函数请使用参考xz_f10指令集说明,参数设置后不能立刻进行mac加密
import serial
import binascii
import re
import time
import logging
import debug
logger = logging.getLogger('pos.log') 
class keypad():
    baud_rate = 9600
    device_name = ''
    timeout = 0.2
    ser = None
    value2key = {'31':'1','32':'2','33':'3','34':'4',
               '35':'5','36':'6','37':'7','38':'8',
               '39':'9','2e':'.','30':'0','08':'backup',
               '1b':'return','21':'up','22':'down','0d':'confirm'}
    pindata = ''
    @staticmethod
    def opencom(device_name):
        try:
            keypad.ser = serial.Serial(device_name,keypad.baud_rate,timeout = keypad.timeout)
            if keypad.ser.isOpen():
                if keypad.getversion():
                    keypad.device_name = device_name
                    logger.info('open right com:' + keypad.device_name)
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
            if keypad.opencom('/dev/ttyUSB0') == False:
                if keypad.opencom('/dev/ttyUSB1') == False:
                    if keypad.opencom('/dev/ttyUSB2') == False:
                        if keypad.opencom('COM2') == False:
                            logger.error('open com failed')
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
            datarcv = keypad.ser.read(1024)
            datarcv = binascii.b2a_hex(datarcv)
            datarcv = keypad.combinecmd(datarcv)
            return datarcv
        except Exception, e:
            logger.error('send or recv cmd failed')
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
        num = len(data)
        if num > 494 or num < 10:
            logger.error('please use auto_mac')
            return False
        else:
            datarcv = keypad._sendcmd( '41' + data )
            if datarcv:
                if datarcv[2:4] == '04':
                    mac_date = datarcv[4:-2]
                    if mac_date[16:] =='0000000000000000':
                        mac_date = mac_date[:16]
                    return mac_date
                else:
                    logger.error('mac return data False')
                    return False
            else:
                logger.error('mac error')
                return False

    @staticmethod
    #mac自动数据运算
    def auto_mac(data):
        newdata = 0
        num = len(data)
        if num > 494:
            data = data + '0'*(16 - num%16)
            try:
                datalist = re.findall(r'(.{16})',data)

                for i in datalist:
                    newdata = newdata ^ int(i,16)

                newdata = hex(newdata)[2:]
                if len(newdata) < 10:
                    newdata = '0'*(16-len(newdata)) + newdata
                if newdata[-1] == 'L' or newdata[-1] == 'l':
                    newdata = newdata[:-1]
            except Exception, e:
                logger.error(e)
        elif num < 10:
            newdata = '0'*(16 - num) + newdata    
        else:
            if len(data)%2 == 1:
                newdata = data + '0'
                logger.error('mac data is not even')
            else:
                newdata = data  
        result = keypad.mac_encrypt(newdata)
        return result

    @staticmethod
    #1.13 取键盘中密码
    def get_encryptpin():
        datarcv = keypad._sendcmd('42')
        if datarcv:
            if datarcv[2:4] == '04':
                return datarcv[4:-12]
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
    #1.25 获取国密模式
    def get_mode():
        datarcv = keypad._sendcmd('91')
        if datarcv:
            if datarcv[2:4] == '04':
                return datarcv[4:6]
            else:
                return False
        else:
            return False
    
    @staticmethod 
    #获取键盘的明文值   
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
            logger.error(e)

    def rcvpindata():
        if keypad.open_encryptkeypad():
            num = 0
            for i in range (100):
                data = keypad.ser.read(4)
                if data:
                    num = num + 1
                if num == 6:
                    break
                if i == 99:
                    #未输入密码
                    return '02' 
            data = keypad.get_encryptpin()
            if data:
                return data
            else:
                return '01'
        else:
            #打开加密键盘失败或者工作不正常
            return '01'
        
if __name__=='__main__':
    if keypad.com_detect():
        keypad.getversion()
        keypad.operate_keypad()
        keypad.operate_keypad('00')
        print 'loadmk:',keypad.loadmk('00','6725A7EACB0EDC49C2087FEF9D2A1F7C')
        keypad.setparameter('00','30')
        print 'loadwk:',keypad.loadwk('00','00','25C7C9E139252CFDF7C4853AC085C19B')

        # mac begin
        print 'active_wk:',keypad.active_wk('00','00')
        keypad.setparameter('01','20')
        keypad.setparameter('06','04')

        # keypad.get_mode()
        print 'automac:',keypad.auto_mac('0200b02004c000c0921100000000000000001900000000000000109200630510820635383439483633363330323434303335303732353834393135366eeaae5cf186af2c9f2608df2411a88d8f985a9f2701809f101307010103a0a000010a01000000000051ca97b59f3704600585359f360200c99505800004f8009a031512159c01609f02060000000000105f2a02015682027c009f1a0201569f03060000000000009f3303e040002292006300050')
        print 'mac:',keypad.mac_encrypt('0200b02004c000c0921100000000000000001900000000000000109200630510820635383439483633363330323434303335303732353834393135366eeaae5cf186af2c9f2608df2411a88d8f985a9f2701809f101307010103a0a000010a01000000000051ca97b59f3704600585359f360200c99505800004f8009a031512159c01609f02060000000000105f2a02015682027c009f1a0201569f03060000000000009f3303e040002292006300050')
        # mac end 
        '''
        print 'data_encrypt:',keypad.data_encrypt('3132333435363738')
        print 'data_decode:',keypad.data_decode('3132333435363738')

        #test pin encrypt
        print 'active_wk:',keypad.active_wk('00','00')
        keypad.setparameter('02','00')
        keypad.setparameter('01','20')
        keypad.setparameter('05','01')
        keypad.setparameter('04','10')
        keypad.setaccount('990123456789')
        keypad.operate_keypad('02')
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
        '''
    else:
        'connect error'    
        



