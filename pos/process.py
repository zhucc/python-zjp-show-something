#!/usr/bin/python
# -*- coding: utf-8 -*-
#filename:process.py
from A6CRTAPI import A6
from apdu import * 
from read_application import *
import time
class pro():
    tvrvalue=['0','0','0','0','0','0','0','0',
              '0','0','0','0','0','0','0','0',
              '0','0','0','0','0','0','0','0',
              '0','0','0','0','0','0','0','0',
              '0','0','0','0','0','0','0','0',]
    nowdate = int(time.strftime("%y%m%d",time.localtime()),10) 
    limitmoney = 0
    gactype = ''
    responsecode = ''
    terminalversion = '0030'
    read_app.tag2value['9f03'] = '000000000000'
    read_app.tag2value['9f1a'] = '0156'
    hospitalname = '6368696E61756E696F6E7061792E616263643132'
    machineproperty = 'e04000'
    read_app.tag2value['9f33'] = machineproperty
    packdata = ''
    @staticmethod
    #根据cdol1组装gac data
    def gacpackage():
        a = time.localtime()
        sdate = time.strftime("%y%m%d",a)
        stime = time.strftime("%H%M%S",a)
        stvr = ''.join(pro.tvrvalue)
        pro.tvrvalue = format(int(stvr,2),'x')
        pro.tvrvalue = ('0'*(6-len(pro.tvrvalue))) + pro.tvrvalue
        #授权金额
        read_app.tag2value['9f02'] = '000000000005'
        #其他金额
        read_app.tag2value['9f03'] = '000000000000'
        read_app.tag2value['9f1a'] = '0156'
        read_app.tag2value['95']   = pro.tvrvalue
        read_app.tag2value['5f2a'] = '0156'
        read_app.tag2value['9a']   = sdate
        #交易类型：国内商品服务
        read_app.tag2value['9c']   = '60'
        #不可预知数
        read_app.tag2value['9f37'] = '60058535'
        read_app.tag2value['9f21'] = stime
        #商户名称
        read_app.tag2value['9f4e'] = pro.hospitalname
        read_app.getcdol1()
        cdol1data = ''
        try:
            for k,v in read_app.cdol1.items():
                cdol1data = cdol1data + read_app.tag2value[k]
        except Exception, e:
            raise e
        return cdol1data
    
    @staticmethod
    #应用选择
    def choseapp():
        aid = read_app.psefunction()
        if aid == False:
            aid = read_app.aidfunction()
        data = APDU.select(aid)
        if data[-4:] == '9000':
            spdol = read_app.pdol(data)
            return spdol
        else: 
            return False


    @staticmethod
    #应用初始化,
    def initapp(spdol):
        data = APDU.gpo(spdol)
        if data[-4:] == '9000':
            return data
        else:
            return False 
    
    @staticmethod
    #读取应用数据
    def readapp(data):
        sfilist = read_app.afl(data)
        for i in sfilist:
            result = APDU.read_record(i)
            if result[-4:] == '9000':
                read_app.analyserecord(result)
            else:
                pass

    @staticmethod
    #脱机数据认证
    def offline():
        #未进行脱机数据认证 
        pro.tvrvalue[0] = '1'    

    @staticmethod
    #处理限制
    def processlimit():
        #应用版本检查
        if (pro.terminalversion != '')and('9f08' in  read_app.tag2value):
            if (pro.terminalversion != read_app.tag2value['9f08']):
                pro.tvrvalue[8] = '1'
        #应用用途和发卡行国家代码检查
        if ('9f07' in read_app.tag2value)and('5f28' in read_app.tag2value):
            auc = read_app.tag2value['9f07']
            auc = bin(int(auc,16))[2:]
            if (auc[0] is '0')or(auc[2] is '0')or(auc[7] is '0'):
                pro.tvrvalue[11] = '1'
        #检查生效日期
        if ('5f25' in read_app.tag2value):
            startdate = int(read_app.tag2value['5f25'],10)
            if startdate > pro.nowdate:
                pro.tvrvalue[10] = '1'  
        #检查失效日期     
        if ('5f24' in read_app.tag2value):
            enddate = int(read_app.tag2value['5f24'],10)
            if enddate < pro.nowdate:
                pro.tvrvalue[9] = '1'
    @staticmethod
    #联机pin验证
    def pinverify(pindata):
        pro.tvrvalue[21] = '1'
        read_app.tag2value['9f26'] = pindata

    @staticmethod
    #终端风险管理
    def riskmanage():
        #终端异常文件检查
        if False:
            pro.tvrvalue[3] = '1'
        #商户要求强制联机
        pro.tvrvalue[28] = '1'
        #终端没有交易流水日志
        #终端最低限额检查
        spendingmoney = int(read_app.pdolvalue['9f02'],10)
        if spendingmoney > pro.limitmoney:
            pro.tvrvalue[24] = '1'
        #随机交易选为联机处理
        pro.tvrvalue[27] = '1'
        #频度检查
        if ('9f14' in read_app.tag2value)and('9f23' in read_app.tag2value):
            read_app.getdata('9f36')
            read_app.getdata('9f13')
            if ('9f13' in read_app.tag2value)and('9f36' in read_app.tag2value):
                atc =  read_app.tag2value['9f36']
                lastatc = read_app.tag2value['9f13']
                minusatc = int(atc,16) - int(lastatc,16)
                maxlimit = int(read_app.tag2value['9f23'],16)
                minlimit = int(read_app.tag2value['9f14'],16)
                if minusatc > maxlimit:
                    pro.tvrvalue[26] = '1'
                if minusatc > minlimit:
                    pro.tvrvalue[25] = '1'
                if  int(lastatc,16) == 0:
                    pro.tvrvalue[12] = '1'
            else:
                pro.tvrvalue[2] = '1'
                pro.tvrvalue[25] = '1'
                pro.tvrvalue[26] = '1'

    @staticmethod
    #终端行为分析
    def behavioranalyse():
        #iacrefuse 与 tvr比较
        if '9f0e' in  read_app.tag2value:
            iacrefuse = bin(int(read_app.tag2value['9f0e'],16))[2:]
            iacrefuse = ('0'*(40-len(iacrefuse))) + iacrefuse
            for i in range (40):
                if (iacrefuse[i]=='1')and(pro.tvrvalue[i]=='1'):
                    #AAC
                    pro.gactype = '00'
                    pro.responsecode = 'Z1'
                    break
                else: 
                    #ARQC
                    pro.gactype = '80'

        else:
            iacrefuse = '0000000000000000000000000000000000000000'
            #ARQC
            pro.gactype = '80'
        #print iacrefuse
        #print ''.join(pro.tvrvalue)
        #发送gac命令
        gacdata = pro.gacpackage()
        result = APDU.generate_ac(pro.gactype,gacdata)
        return result
    
    @staticmethod
    #'88'转成'10001000'
    def hex2bin(data):
        all_length = len(data)*4
        bindata = bin(int(data,16))[2:]
        lastlength = all_length - len(bindata)
        bindata = '0'*lastlength + bindata
        return bindata

    @staticmethod
    #打包不变二进制数
    def packbintag(tag):
        value = read_app.tag2value[tag]
        value = pro.hex2bin(value)
        pro.packdata  = pro.packdata + tag + value

    @staticmethod
    #打包不变bcd或ascii数
    def packbcdtag(tag):
        value = read_app.tag2value[tag]
        if (tag == '5f2a') or (tag == '9f1a'):
            value = value[1:]
        pro.packdata  = pro.packdata + tag + value

    @staticmethod
    #打包可变二进制数
    def packvarbintag(tag):
        value = read_app.tag2value[tag]
        value = pro.hex2bin(value)
        num = len(value)
        slength = format(num,'x')
        if num < 16:
            slength = '0' + slength
        pro.packdata  = pro.packdata + tag + slength + value

    @staticmethod
    #打包数据给报文
    def package():
        data = ''
        try:
            pro.packbintag('9f26')
            pro.packbintag('9f27')
            pro.packvarbintag('9f10')
            pro.packbintag('9f37')
            pro.packbintag('9f36')
            pro.packbintag('95')
            pro.packbcdtag('9a')
            pro.packbcdtag('9c')
            pro.packbcdtag('9f02')
            pro.packbcdtag('5f2a')
            pro.packbintag('82')
            pro.packbcdtag('9f1a')
            pro.packbcdtag('9f03')
            pro.packbintag('9f33')
            return True
        except Exception, e:
            raise e
            pro.packdata = ''
            return False


    

    @staticmethod
    #联机交易
    def online():
        pass

    @staticmethod
    #交易结束
    def closetransaction():
        pass


if __name__ == '__main__':
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

                pro.online()
                pro.closetransaction()       
    else:
        print('connect error')
