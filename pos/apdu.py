#!/usr/bin/python
# -*- coding: utf-8 -*-
#filename:apdu.py
from A6CRTAPI import A6

class APDU():
    '''
    gpo(s_pdolvalue)
    read_record(string)
    getdata(tag)

    '''
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
        result = A6.CpuTransmit(cmd)
        return result

    @staticmethod
    #string = p1+p2 = number + SFI
    def read_record(string):
        cmd = '00B2'
        cmd = cmd + string + '00'
        result = A6.CpuTransmit(cmd)
        return result

    @staticmethod
    #获取标签的数据
    def getdata(tag):
        cmd = '80CA'
        cmd = cmd + tag + '00'
        result = A6.CpuTransmit(cmd)
        return result

    @staticmethod
    def select (address):
        cmd = '00A40400'
        slen1 = APDU._len2str(address)
        cmd = cmd + slen1 + address + '00'
        result = A6.CpuTransmit(cmd)
        return result

    @staticmethod
    def generate_ac(type,data):
        slen1 = APDU._len2str(data)
        cmd = '80AE' + type + '00' + slen1 + data + '00'
        result = A6.CpuTransmit(cmd)
        return result
     
    @staticmethod
    def internal_authenticate(data):
        slen1 = APDU._len2str(data)
        cmd = '00880000' + slen1 + data + '00'
        result = A6.CpuTransmit(cmd)
        return result

if __name__ == '__main__':
    from A6CRTAPI import *
    communication = APDU.select('315041592E5359532E4444463031')
    communication2 = A6.CpuTransmit('00A404000e315041592E5359532E444446303100')