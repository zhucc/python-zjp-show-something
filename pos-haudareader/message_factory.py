#!/usr/bin/python
# -*- coding: utf-8 -*-
#filename:message_factory.py
import logging
import debug
from metal_keypad import keypad
import binascii
from read_application import read_app
from ic_reader import ic
from metal_keypad import keypad
import time
from file_operate import FILE
#MF--message_factory,负责组装出完整的报文，解析收到的完整报文
#转码规则：奇数bcd一般右补0，二进制转为16进制字符串，ascii格式要转为ascii码
logger = logging.getLogger('pos.log') 
class MF():
    message_dict = {} 
    tpdu = '6005108067'
    dial = '4C5249001C' + '0000075588318355' + '0000000060847260'+'580009490006000000C20146'
    header = '60'+'21'+'10'+ '000000' #正常交易改为00
    data11_filename = 'd:\\consume.txt'
    consume_data = '000000000010' 
    data55 = ''
    checkinlist = ['11','41','42','60']
    consumelist = ['2','3','4','11','22','25','26','35','41','42','49','52','55','60','64']
    reversallist = ['3','4','11','22','25','35','39','41','42','49','55','60','61','64']
    @staticmethod
    #输入一个16进制字符串，转化为ascii码，字母的值按照大写输出  
    def str2ascii(string):
        asciivalue = ''
        try:
            string = string.upper()
            for i in range (len(string)):
                num = hex(ord(string[0]))[2:]
                asciivalue += num
                string = string[1:]
        except Exception, e:
            logger.error ('str2ascii error:'+ string)
        return asciivalue
     
        
    @staticmethod
    #记录流水号增加,000000--999999
    def _record_add():
        try:
            number = FILE.read(MF.data11_filename,'000000')
            number = int(number,10)
            number += 1
            number = str(number) 
            if number == '1000000':
                number = '000000'
            number = '0'*( 6 - len(number) ) + number
        except Exception, e:
            number = '000000'
        FILE.write(MF.data11_filename,number)
        return number

    @staticmethod
    #记录流水号减少,000000--999999
    def _record_minus():
        try:
            number = FILE.read(MF.data11_filename,'000000')
            number = int(number,10)
            if number == 0:
                number = 999999 + 1
            number -= 1
            number = str(number) 
            number = '0'*(6 - len(number)) + number
        except Exception, e:
            number = '000000'
        FILE.write(MF.data11_filename,number)
        return number
        


    @staticmethod
    #报文组装，输入参数皆为字符串，bitmap_bit 32表示128位
    def linker(message_type,address_list,bitmap_bit = 32):
        message = ''
        bitmap = ['0']*(bitmap_bit*4 + 1)

        bitmap[1] = '1'
        for i in address_list:
            num = int(i,10)
            bitmap[num] = '1'
        del bitmap[0]

        binvalue = ''
        for i in bitmap:
            binvalue = binvalue + i
        bitmaphex = hex(int(binvalue,2))[2:]
        if bitmaphex[-1] == 'L':
            bitmaphex = bitmaphex[:-1]
        bitmaphex = '0'*(bitmap_bit-len(bitmaphex)) + bitmaphex
        logger.info( '8583data component')
        for i in address_list:
            if i in MF.message_dict:
                logger.info( i+':'+MF.message_dict[i])
                message += MF.message_dict[i]    
            else:
                #需要mac加密
                if i == '64':
                    #mac加密的数据组成
                    message = message_type + bitmaphex + message 
                    macdate = keypad.auto_mac(message)
                    #print 'woshimac',message
                    if macdate != False:
                        logger.error('64'+':'+macdate)
                        message = message + macdate
                    else:
                        return False
                else:
                    logger.error ('there is no message:'+ i)
                    return False
            
        message = message_type + bitmaphex + message 
        #求总数据的字节数
        alllength =  str(len(message)/2 + 25)
        alllength = (4-len(alllength))*'0' + alllength
        message = alllength + MF.tpdu + MF.dial + MF.header + message
        logger.info('8583data:' + message)
        return message

    @staticmethod
    #获取可变域的长度值,输入域值（），域长位数(整数),llvar取2，lllvar取4，返回域长+域值
    def _getlength(domain_value,maxbit):
        data = domain_value
        length = len(data)
        if length%2 == 1:
            data = data + '0'
            length = length + 1
        slength = str(length)
        slength = '0'*(maxbit - len(slength)) + slength
        return slength + data

    @staticmethod
    #签到
    def checkin_package():
        MF.checkinlist = ['11','41','42','60']
        data11 = MF._record_add()
        messagetype = '0400'
        MF.checkinlist = ['11','41','42','60']
        MF.message_dict['11'] = data11
        MF.message_dict['41'] = '20292020'
        MF.message_dict['42'] = '123456789012316'
        MF.message_dict['60'] = '00' + data11 + '003'
        message = MF.linker(messagetype,MF.checkinlist)
        num = len(message)
        keypad.com_detect()
        macdate = keypad.auto_mac(message)
        return message
    
    @staticmethod
    #用密码键盘获取密码
    def getpin():
        if keypad.com_detect():
            keypad.active_wk('00','00')
            keypad.setparameter('02','00')
            keypad.setparameter('01','20')
            keypad.setparameter('05','01')
            keypad.setparameter('04','10')
            keypad.setaccount('990123456789')
            keypad.operate_keypad('02')
            keypad.open_encryptkeypad()
            print ('plz press keypad button')
            num = 0
            for i in range (100):
                data = keypad.ser.read(4)
                if data:
                    num = num + 1
                if num == 6:
                    break 
            print('plz wait')
            return keypad.get_encryptpin()
        else:
            return False

    @staticmethod
    #消费
    def consume_package():
        MF.data55 = ic.reader1(MF.consume_data)
        if not MF.data55:
            logger.info( 'domain 55 data lost')
            return False
        print read_app.tag2value
        MF.consumelist = ['2','3','4','11','22','25','26','35','41','42','49','52','55','60','64']
        data11 = MF._record_add()
        messagetype = '0200'
        if '5a' in read_app.tag2value:
            MF.message_dict['2'] = MF._getlength(read_app.tag2value['5a'],2)
        else:
            MF.consumelist.remove('2')
        MF.message_dict['3'] = '190000'
        MF.message_dict['4'] = MF.consume_data #消费金额
        MF.message_dict['11'] = data11
        MF.message_dict['22'] = '0510'
        MF.message_dict['25'] = '82'
        MF.message_dict['26'] = '06'
        if '57' in read_app.tag2value:
            MF.message_dict['35'] = MF._getlength(read_app.tag2value['57'],2)
        else:
            MF.consumelist.remove('35')
        #无法读取3磁道等效信息
        MF.message_dict['41'] = MF.str2ascii('5849H636')
        MF.message_dict['42'] = MF.str2ascii('302440350725849')
        MF.message_dict['49'] = MF.str2ascii('156')
        MF.message_dict['52'] = MF.getpin() #金属键盘调用
        MF.message_dict['55'] = MF._getlength(MF.data55,4)
        MF.message_dict['60'] = MF._getlength('22' + data11 + '00000050',4)
        message = MF.linker(messagetype,MF.consumelist)
        return message 

    @staticmethod
    #冲正
    def reversal_package():
        MF.reversallist = ['3','4','11','22','25','35','39','41','42','49','55','60','61','64']
        sdate = time.strftime("%m%d",time.localtime())
        data11 = FILE.read(MF.data11_filename,'000000')
        messagetype = '0800'
        MF.message_dict['3'] = '190000'
        MF.message_dict['4'] = MF.consume_data #消费金额
        MF.message_dict['11'] = data11
        MF.message_dict['22'] = '0510'
        MF.message_dict['25'] = '82'
        if '57' in read_app.tag2value:
            MF.message_dict['35'] = read_app.tag2value['57']
        else:
            reversallist.remove('35')
        #无法读取3磁道等效信息
        MF.message_dict['39'] = '96'
        #默认为96，终端收到多渠道平台的批准应答消息，但由于故障无法完成交易
        MF.message_dict['41'] = MF.str2ascii('5849H636')
        MF.message_dict['42'] = MF.str2ascii('302440350725849')
        MF.message_dict['49'] = MF.str2ascii('156')
        MF.message_dict['55'] = MF.data55
        MF.message_dict['60'] = '22' + data11 + '00050'#60.4与60.5不用
        MF.message_dict['61'] = data11 + data11 + sdate + '0000000000000' 
        message = MF.linker(messagetype,reversallist)
        return message  

    
        


if __name__ == '__main__':
  
    #print MF.checkin_package()
    print MF.consume_package()
    #print MF.reversal_package()
    