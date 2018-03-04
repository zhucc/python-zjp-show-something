#!/usr/bin/python
# -*- coding: utf-8 -*-
#filename:read_application.py
from multifunction_reader import reader
from apdu import * 
import re
import collections
import logging
logger = logging.getLogger('pos.log') 
class read_app():
    #查找键值时一律小写，大写是找不到的
    posdata={'9f09':0030}
    pdolvalue = {'9f7a':'00','9f02':'000000000005','5f2a':'0156'}
    #readrecord后卡片必须返回的数据
    dictmustdata = {'5f24':'0','5a':'0','8c':'0','8d':'0'}
    #卡片返回的数据均以tag:value 的形式存在这里
    tag2value={}
    aiddit= {}         
    cdol1 = collections.OrderedDict()

    @staticmethod
    #解析出一个tlv字符串 ，加入tag2value字典中，返回未解析的部分
    def analyse_tlv_once(tag,tlvdata):
        if tlvdata:
            #截取长度
            firstbyte = tlvdata[:2]
            #如果bit8为0,第一个字节为长度
            firstnum = int(firstbyte,16)
            temp = firstnum
            if ( temp & 128) == 0 :
                length = firstnum
                tlvdata = tlvdata[2:]
            else:
                #长度值占用的字节数
                temp = firstnum & 127
                length = int(tlvdata[2:2+2*temp],16)
                tlvdata = tlvdata[2+2*temp:]
            #截取标签的数值
            value = tlvdata[:length*2]
            tlvdata[:length*2]
            read_app.tag2value[tag] = value
            #print 'tag:',tag,'value:',value
            return tlvdata[length*2:] 
        else:
            logger.error('tlv data error' + tlvdata)
            return ''

    @staticmethod
    #解析times次tlv,递归最大深度为8,第一层标签最多为15个
    def analyse_tlv(tlvdata,deep = 0,times = 15):
        try:
            for i in range(times):
                if tlvdata =='9000' or tlvdata == '':
                    break
                #截取标签
                firstbyte = tlvdata[:2]
                #bit1-5全为1表示双字节00
                if (int(firstbyte,16) & 31) == 31 :
                    tag = tlvdata[:4]
                    tlvdata = tlvdata[4:]
                else:
                    tag = tlvdata[:2]
                    tlvdata = tlvdata[2:]
                tlvdata = read_app.analyse_tlv_once(tag,tlvdata)
            #复合数据，value的值需要再解析
            if (int(tag[:2],16)) & 0x20:
                value = read_app.tag2value[tag]
                deep = deep + 1 
                #最多递归8次
                if deep < 8:
                    read_app.analyse_tlv(value,deep)
                    del read_app.tag2value[tag]
                else:
                    logger.error('analyse_tlv out of deep ')   
            #单一结构数据,value不需要再解析
            else:
                pass
        except Exception, e:
            logger.error(e) 
            

        

    @staticmethod
    #aid列表方法
    def aidfunction():
        #aid包含了借记卡08a000000333010101和贷记卡08a000000333010102
        aid = '07a0000003330101'
        return aid 
    
    @staticmethod
    #'88'转成'10001000'
    def hex2bin(data):
        all_length = len(data)*4
        bindata = bin(int(data,16))[2:]
        lastlength = all_length - len(bindata)
        bindata = '0'*lastlength + bindata
        return bindata
    
    @staticmethod
    #目录方法构件，pse 中的 sfi获取
    def psesfi(result):
        read_app.analyse_tlv(result,0)
        if '88' in read_app.tag2value:
            num = int(read_app.tag2value['88'],16)
            #高三位为0
            sfi = hex((num<<3) + (1<<2))[2:]
            if len(sfi) == 1:
                sfi = '0' + sfi
            elif len(sfi) >2:
                sfi = sfi[-2:]
            else:
                pass
            return sfi
        else:
            logger.info('pse data lost sfi :tag 88')
            return False

    @staticmethod
    #目录方法
    def psefunction():
        # 315041592E5359532E4444463031  >>  1PAY.SYS.DDF01 的ascii
        pse_address = '315041592E5359532E4444463031'
        data = APDU.select(pse_address)
        if data != False:
            #判断是否读到pse的地址
            sfi = read_app.psesfi(data)
            if sfi:
                #根据pse地址读出所有aid并加入到aid字典中，返回优先级最高的aid
                for i in range(1,20):
                    snum = APDU._num2str(i)
                    result = APDU.read_record(snum + sfi)
                    if result == '6a83':
                        logger.info('end of reading aid with pse ')
                        break
                    elif result == False:
                        logger.error('communication error')
                        break
                    else:
                        read_app.analyse_tlv(result,0)
                        #读完一条记录，记录应用和优先级
                        if '4f' in  read_app.tag2value:
                            if '87' in  read_app.tag2value:
                                #读出优先级
                                value = read_app.tag2value['87']
                                value = read_app.hex2bin(value)[-4:]
                                value = str(int(value,2))
                            else:
                                #不指定优先级则默认为2
                                value = '2'
                            read_app.aiddit[value] = read_app.tag2value['4f'] 
                        else:
                             logger.info('record'+ snum +'has no aid')         
                   
                if len(read_app.aiddit):
                    #返回应用优先级最高的aid
                    return read_app.aiddit['1']
                else:
                    #aid读取失败
                    logger.error('found no aid in pse')
                    return False
            else:
                logger.error('pes address error')
                #pse地址读取失败
                return False
        else:
            logger.error('can not select pse')
            #选择pse返回失败
            return False

    @staticmethod
    #输入9f38的值返回填充好的pdol
    def process9f38(data):
        spdol = ''
        for i in range (len(data)/6):
            try:
                tag = data[:4]
                value = read_app.pdolvalue[tag]
                if len(value) == int(data[4:6],16)*2:
                    spdol = spdol + value
                    data = data[6:]
                else:
                    logger.error('read_app.pdolvalue:'+ tag + 'length error')
                    return False
            except Exception, e:
                logger.error(e)
                return False
        return spdol
   

    @staticmethod
    #输入选择aid后卡片返回的值，返回填充好的pdol
    def pdol(result):
        read_app.analyse_tlv(result,0)
        if '9f38' in read_app.tag2value:
            pdollist = read_app.tag2value['9f38']
            spdol = read_app.process9f38(pdollist)
            return spdol
            logger.info('make pdol success')
        else:
            logger.error('select aid and return data without pdollist 9f38')
            return False

    @staticmethod
    #data为afl的第一个字节,sfi 低三位为0
    def sfidecode(data):
        num = int(data,16)
        num = num + 4 #100
        sfi = format(num,'x')
        if num < 16:
            sfi = '0' +sfi
        return sfi

    @staticmethod
    def afl(data):
        try:
            read_app.analyse_tlv(data,0)
            #80开头的数据类型
            if '80' in  read_app.tag2value:
                read_app.tag2value['82'] = read_app.tag2value['80'][0:4]
                aflstr = read_app.tag2value['80'][4:]
                del read_app.tag2value['80']
            #77开头的数据类型 
            elif '94' and '82' in  read_app.tag2value:
                aflstr = read_app.tag2value['94']
            else:
                logger.error('gpo return data without afl or aip')
                return False
            #每个afl有4字节 sfi+first+last+static
            afllist = re.findall(r'(.{8})',aflstr)
            num = len(afllist)
            sfilist = []
            for i in range(num):
                afl = afllist[i]
                sfi = afl[:2]
                first = afl[2:4]
                last = afl[4:6]
                staticnumber =afl[6:] 
                sfi = read_app.sfidecode(sfi)
                for i in range(1,10):
                    i =  '0' + format (i,'x')
                    recordaddress = i + sfi
                    sfilist.append(recordaddress)
                    if i == last:
                        break
            return sfilist
        except Exception, e:
            logger.error(e)
            return False 
                  
    @staticmethod
    #'9f02069f03069f1a0295055f2a029a039c019f37049f21039f4e14'转换成
    #{'9f1a': 2, '9a': 3, '9c': 1, '5f2a': 2, '9f37': 4, '9f03': 6, '9f02': 6, '9f4e': 20, '95': 5, '9f21': 3}
    def getcdol1():
        cdoldata = read_app.tag2value['8c']
        for i in range (40):
            cdoltag = cdoldata[:2]
            if cdoltag != '':
                if (cdoltag[1] == 'f') :
                    cdoltag = cdoldata[:4]
                    cdoldata = cdoldata[4:]
                else:
                    cdoldata = cdoldata[2:]
                slength = cdoldata[:2]
                byte = int(slength,16)
                read_app.cdol1[cdoltag] = byte
                cdoldata = cdoldata[2:]
            else:
                break


    @staticmethod
    def getdata(tag):
        data = APDU.getdata(tag)
        if data[-4:] =='9000':
            read_app.analyse_tlv(data)
        else:
            pass




if __name__ == '__main__':
    if  reader.com_detect():
        reader.cpu_coldreset()
        aid = read_app.psefunction()
        if aid == False:
            aid = read_app.aidfunction()   
        data = APDU.select(aid)
        if data:
            spdolvalue = read_app.pdol(data) 
            data = APDU.gpo(spdolvalue)
            if data:
                afllist = read_app.afl(data)
                if afllist:
                    for i in afllist:
                        result = APDU.read_record(i)
                        if result:
                            read_app.analyse_tlv(result,0)
                            #print read_app.tag2value
                        else:
                            logger.info('record' + i + 'return False')
                    if '8c' in read_app.tag2value:
                        read_app.getcdol1()
                    print read_app.tag2value
                else:
                    logger.error('afllist is error')
            else:
                logger.error('gpo return False')
        else:
            logger.error('consume failed')       
    else:
        print('connect error')