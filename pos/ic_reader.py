#!/usr/bin/python
# -*- coding: utf-8 -*-
#filename:ic_reader.py
from process import *
from A6CRTAPI import A6
from apdu import * 
from read_application import *
class ic():
    @staticmethod
    def reader1(moneystr):
        read_app.pdolvalue['9f02'] = moneystr
        connect_result = A6.Connect(2,9600)
        if  connect_result[0] is 0:
            hReader = connect_result[1]
            #A6_LedOn(hReader)
            A6.LedBlink(10,30)
            A6.SetCardIn()
            A6.SetDockedPos()
            #print (A6.MoveCard()) 
            A6.IccPowerOn()
            A6.DetectIccType()
            A6.CpuColdReset()
            spdol = pro.choseapp()
            if spdol:
                data = pro.initapp(spdol)
                if data:
                    pro.readapp(data)
                    if '9f14' in read_app.tag2value:
                        read_app.getdata('9f13')
                    if '9f23' in read_app.tag2value:
                        read_app.getdata('9f36')
                    read_app.getdata('9f13')
                    read_app.getdata('9f17')
                    read_app.getdata('9f36')
                    pro.offline()
                    pro.processlimit()
                    pro.pinverify('pinmac')
                    pro.riskmanage()
                    data = pro.behavioranalyse()
                    result = read_app.analysegac(data)
                    print  read_app.tag2value
                    if pro.package():
                        return pro.packdata
                    else:
                        print('data pack error')
                else:
                    print('gpo return error')
            else:
                print('no pdol')
        else:
            print('connect error')
           
    @staticmethod   
    def reader2(): 
        pass


if __name__ == '__main__':
    a = ic.reader1('000000000010')
    print len(a)
    print a
    ic.reader2()
