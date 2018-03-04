#!/usr/bin/python
# -*- coding: utf-8 -*-
#filename:ic_reader.py
from process import *
from multifunction_reader import reader
from apdu import * 
from read_application import *
import logging
import debug
logger = logging.getLogger('pos.log') 
class ic():
    @staticmethod
    def reader1(moneystr):
        read_app.tag2value['9f02'] = moneystr
        if  reader.com_detect():
            reader.cpu_coldreset()
            spdol = pro.choseapp()
            if spdol:
                data = pro.initapp(spdol)
                if data:
                    pro.readapp(data)
                    pro.offline()
                    pro.processlimit()
                    pro.verify_function()
                    pro.riskmanage()
                    data = pro.behavioranalyse()
                    result = pro.analysegac(data)
                    print 'analysegac:',result
                    print  read_app.tag2value
                    if pro.package():
                        return pro.packdata
                    else:
                        return False
                else:
                    return False
            else:
                return False
        else:
            return False
           
    @staticmethod   
    def reader2(): 
        pass


if __name__ == '__main__':
    
    
    a = ic.reader1('000000000010')
    print a
    
