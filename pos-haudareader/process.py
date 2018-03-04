#!/usr/bin/python
# -*- coding: utf-8 -*-
#filename:process.py
from multifunction_reader import reader
from apdu import * 
from read_application import *
import time
import logging
import debug
import time
from functools import wraps
logger = logging.getLogger('pos.log')  
def fn_timer(function):
    @wraps(function)
    def function_timer(*args, **kwargs):
        t0 = time.time()
        result = function(*args, **kwargs)
        t1 = time.time()
        print ("Total time running %s: %s seconds" %
            (function.func_name, str(t1-t0)))
        return result
    return function_timer
    

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
    terminalversion = ''
    country = ''
    read_app.tag2value['9f03'] = '000000000000'
    read_app.tag2value['9f1a'] = '0156'
    hospitalname = '6368696E61756E696F6E7061792E616263643132'
    machineproperty = 'e04000'
    read_app.tag2value['9f33'] = machineproperty
    packdata = ''

    #开机时候需要pos初始化的常量
    @staticmethod
    def initpos():
        pro.terminalversion = '0030'
        pro.country = '0156'

        
    @staticmethod
    #根据cdol1组装gac data
    def gacpackage():
        a = time.localtime()
        sdate = time.strftime("%y%m%d",a)
        stime = time.strftime("%H%M%S",a)
        stvr = ''.join(pro.tvrvalue)
        pro.tvrvalue = format(int(stvr,2),'x')
        pro.tvrvalue = ('0'*(6-len(pro.tvrvalue))) + pro.tvrvalue
        #授权金额,放到ic_reader里
        #read_app.tag2value['9f02'] = '000000000005'
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
            logger.error(e) 
        return cdol1data
    
    @staticmethod
    #应用选择
    @fn_timer
    def choseapp():
        aid = read_app.psefunction()
        if aid == False:
            aid = read_app.aidfunction()   
        data = APDU.select(aid)
        if data:
            spdol = read_app.pdol(data)
            return spdol
        else: 
            logger.error('select aid failed')
            return False
       

    @staticmethod
    #应用初始化,
    @fn_timer
    def initapp(spdol):
        data = APDU.gpo(spdol)
        if data:
            return data
        else:
            logger.error('gpo failed')
            return False 
    
    @staticmethod
    #读取应用数据
    @fn_timer
    def readapp(data):
        sfilist = read_app.afl(data)
        if sfilist:
            for i in sfilist:
                result = APDU.read_record(i)
                if result:
                    read_app.analyse_tlv(result)
                    #print read_app.tag2value
                else:
                    logger.info('record' + i + 'return False')

    @staticmethod
    #脱机数据认证
    def offline():
        #未进行脱机数据认证 
        pro.tvrvalue[0] = '1'    

    @staticmethod
    #处理限制
    @fn_timer
    def processlimit():
        try:
            #应用版本检查
            if (pro.terminalversion != '')and('9f08' in  read_app.tag2value):
                if (pro.terminalversion != read_app.tag2value['9f08']):
                    pro.tvrvalue[15] = '1'
                else:
                    logger.info('app lication version different')
            else:
                logger.info('application version infomation lost')
            #应用用途和发卡行国家代码检查
            if ('9f07' in read_app.tag2value):
                auc = bin(int(read_app.tag2value['9f07'],16))[2:]
                if auc[0] == '0':
                    #不支持atm以外的终端
                    pro.tvrvalue[12] = '1'
                elif ('5f28' in read_app.tag2value):
                    #默认是消费交易
                    #国内
                    if read_app.tag2value['5f28'] == pro.country:
                        if (auc[3] == '0') and (auc[5] == '0'):
                            pro.tvrvalue[12] = '1'
                    #国际
                    else:
                        if (auc[2] == '0') and (auc[4] == '0'):
                            pro.tvrvalue[12] = '1':
                    
            #检查生效日期
            if ('5f25' in read_app.tag2value):
                startdate = int(read_app.tag2value['5f25'],10)
                if startdate > pro.nowdate:
                    pro.tvrvalue[13] = '1'  
            #检查失效日期     
            if ('5f24' in read_app.tag2value):
                enddate = int(read_app.tag2value['5f24'],10)
                if enddate < pro.nowdate:
                    pro.tvrvalue[14] = '1'
        except Exception, e:
            logger.error(e) 
            

    @staticmethod
    #持卡人方法验证
    def verify_function(pindata):
        #卡片有应用交互特征并且bit5是1(支持持卡人认证)
        if ('82' in read_app.tag2value)and(int(read_app.tag2value['82'],16)&0x10 == 0x10):
            if '8e' in read_app.tag2value:
                cvmlist = re.findall(r'(.{4})',read_app.tag2value['8e'][16:])
                for i in cvmlist:
                    cvmtype = read_app.hex2bin(i[:2])
                    if cvmtype[:6]=='000010':
                        #执行联机pin
                    else:
                        if int(i,16)&0x40:
                            pass
                        else:
                            break
                        #验证失败        
            else:
                pro.tvrvalue[5] = '1'
        else:
            pass

        else:
            pro.tvrvalue[21] = '1'
        read_app.tag2value['9f26'] = pindata

    @staticmethod
    #终端风险管理
    @fn_timer
    def riskmanage():
        try:
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
        except Exception, e:
            logger.info(e)
        

    @staticmethod
    #终端行为分析
    @fn_timer
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
    #打包
    def packtag(tag):
        value = read_app.tag2value[tag]
        num = (len(value)+1)/2
        slength = format(num,'x')
        if num < 16:
            slength = '0' + slength
        pro.packdata  = pro.packdata  + tag + slength + value

    @staticmethod
    #打包数据给报文
    def package(address55list = ['9f26','9f27','9f10','9f37','9f36','95','9a','9c','9f02','5f2a','82','9f1a','9f03','9f33']):
        try:
            for i in address55list:
                pro.packtag(i)
                logger.info(i +':'+ read_app.tag2value[i])
            data55 = pro.packdata
            length =str( (len(data55) + 1)/2 )
            pro.packdata = '0'*(4 - len(length)) + length + pro.packdata

            return True
        except Exception, e:
            logger.error(e)
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


    if  reader.com_detect():
        reader.cpu_coldreset()
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
