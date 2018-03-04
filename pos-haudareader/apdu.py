#!/usr/bin/python
# -*- coding: utf-8 -*-
#filename:apdu.py
from multifunction_reader import reader
import logging
logger = logging.getLogger('pos.log') 
class APDU():

    @staticmethod
    def _num2str(num):
        snum = format(num,'x')
        if num < 16:
            snum = '0' + snum
        return snum

    @staticmethod
    #获取字符串的长度16进制值
    def _len2str(string):
        length = len(string)/2 
        return APDU._num2str(length)
    
    @staticmethod
    def gpo(s_pdolvalue):
        #s_pdolvalue = pdol列表中的值组成字符串
        cmd = '80A80000'
        slen2 = APDU._len2str(s_pdolvalue)
        slen1 = APDU._len2str(s_pdolvalue + '83' + slen2)
        cmd = cmd + slen1 + '83' + slen2 + s_pdolvalue +'00'   
        #PDOL通过标签“83”标记
        result = reader.cpu_apdu(cmd)
        if result:
            if result[-4:] == '9000':
                return result
            else:
                logger.info('gpo operate failed')
                return False
        else:
            #reader.cpu_apdu会记录错误
            return False

    @staticmethod
    #string = p1+p2 = number + SFI
    def read_record(string):
        cmd = '00B2'
        cmd = cmd + string + '00'
        result = reader.cpu_apdu(cmd)
        if result:
            if result[-4:] == '9000'or '900':
                return result
            else:
                logger.info('read_record operate failed:' + cmd)
                return False
        else:
            #reader.cpu_apdu会记录错误
            return False

    @staticmethod
    #获取标签的数据
    def getdata(tag):
        cmd = '80CA'
        cmd = cmd + tag + '00'
        result = reader.cpu_apdu(cmd)
        return result

    @staticmethod
    def select (address):
        cmd = '00A40400'
        slen1 = APDU._len2str(address)
        cmd = cmd + slen1 + address + '00'
        result = reader.cpu_apdu(cmd)
        if result:
            if result[-4:] == '9000':
                return result
            else:
                logger.info('select operate failed:' + cmd)
                return False
        else:
            #reader.cpu_apdu会记录错误
            return False

    @staticmethod
    def generate_ac(type,data):
        slen1 = APDU._len2str(data)
        cmd = '80AE' + type + '00' + slen1 + data + '00'
        result = reader.cpu_apdu(cmd)
        return result
     
    @staticmethod
    def internal_authenticate(data):
        slen1 = APDU._len2str(data)
        cmd = '00880000' + slen1 + data + '00'
        result = reader.cpu_apdu(cmd)
        return result

if __name__ == '__main__':
    if  reader.com_detect():
        print reader.cpu_coldreset()
        print APDU.select('7378312E73682EC9E7BBE1B1A3D5CF')
        print APDU.read_record('015c')
        print APDU.read_record('025c')
        print APDU.read_record('035c')
        print APDU.read_record('045c')
        print APDU.read_record('055c')
        print APDU.read_record('065c')
        print 'select aid'
        print APDU.select('d15600000500')
        print APDU.gpo('8300')
        '''
        print APDU.select('d15600000501')
        print APDU.select('d15600000502')
        print APDU.select('d15600000503')
        print APDU.select('d15600000504')
        print APDU.select('d15600000505')
        print APDU.select('d1560000050a')
        '''
        print reader.cpu_poweroff()
        #print reader.cpu_apdu('00A404000e315041592E5359532E444446303100')
    else:
        print 'connect error!!'