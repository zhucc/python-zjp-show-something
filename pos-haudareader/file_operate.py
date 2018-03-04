#!/usr/bin/python
# -*- coding: utf-8 -*-
#filename:file_operate.py
import logging
import debug
logger = logging.getLogger('pos.log') 
class FILE():
    @staticmethod
    def write(filename,data):
        try:
            handle = open(filename, 'w')
        except Exception, e:
            logger.error('open file error:'+ filename)
            handle = open(filename, 'a')
            handle.close()
            handle = open(filename, 'w')
        handle.write(data)
        handle.close()
        

    @staticmethod
    #读出文件内的数据,文件不存在则新建文件写入初始化数据
    def read(filename,initdata):
        try:
            handle = open(filename, 'r')
        except Exception, e:
            logger.error(e)
            FILE.write(filename,initdata)  
            handle = open(filename, 'r') 
        data = handle.read()
        handle.close()
        return data    

if __name__ == '__main__':
    filename = 'd://consum1.txt'
    print FILE.read(filename,'87988')
    FILE.write(filename,'11111111111222222\n222222222222222\n22222222\n2222222222\n22222222222\n11111111111111111111')
    
    