#!/usr/bin/python
# -*- coding: utf-8 -*-
#filename:read_application.py
from A6CRTAPI import A6
from apdu import * 
import re
import collections
class read_app():
    #���Ҽ�ֵʱһ��Сд����д���Ҳ�����
    posdata={'9f09':0030}
    pdolvalue = {'9f7a':'00','9f02':'000000000005','5f2a':'0156'}
    #readrecord��Ƭ���뷵�ص�����
    dictmustdata = {'5f24':'0','5a':'0','8c':'0','8d':'0'}
    tag2value={}
    aiddit= {}         
    cdol1 = collections.OrderedDict()
    @staticmethod
    #'9f02069f03069f1a0295055f2a029a039c019f37049f21039f4e14'ת����
    #{'9f1a': 2, '9a': 3, '9c': 1, '5f2a': 2, '9f37': 4, '9f03': 6, '9f02': 6, '9f4e': 20, '95': 5, '9f21': 3}
    def getcdol1():
        cdoldata = read_app.tag2value['8c']
        for i in range (40):
            cdoltag = cdoldata[:2]
            if cdoltag != '':
                if (cdoltag == '9f') or (cdoltag == '5f') or (cdoltag == 'bf'):
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
    #'88'ת��'10001000'
    def hex2bin(data):
        all_length = len(data)*4
        bindata = bin(int(data,16))[2:]
        lastlength = all_length - len(bindata)
        bindata = '0'*lastlength + bindata
        return bindata

    @staticmethod
    #aid�б���
    def aidfunction():
        #aid�����˽�ǿ�08a000000333010101�ʹ��ǿ�08a000000333010102
        aid = '07a0000003330101'
        return aid 

    @staticmethod
    #Ŀ¼����
    def psefunction():
        # 1PAY.SYS.DDF01 ��ascii
        pse_address = '315041592E5359532E4444463031'
        data = APDU.select(pse_address)
        #�ж��Ƿ����pse�ĵ�ַ
        if read_app.psesfi(data):
            #����pse��ַ��������aid�����뵽aid�ֵ��У��������ȼ���ߵ�aid
            for i in range(1,5):
                snum = APDU._num2str(i)
                result = APDU.read_record(snum + read_app.tag2value['88'])
                if result != '6a83':
                    result =result[8:]
                    for i in range (10):
                        if result == '9000'or result == '':
                            break
                        else:
                            result = read_app.gettagvalue(result)
                    #����һ����¼����¼Ӧ�ú����ȼ�
                    if '4f' in  read_app.tag2value:
                        if '87' in  read_app.tag2value:
                            #�������ȼ�
                            value = read_app.tag2value['87']
                            value = read_app.hex2bin(value)[-4:]
                            value = str(int(value,2))
                        else:
                            value = '1'
                        read_app.aiddit[value] = read_app.tag2value['4f'] 
                    else:
                         pass         
                else:
                    break
            if len(read_app.aiddit):
                #����Ӧ�����ȼ���ߵ�aid
                return read_app.aiddit['1']
            else:
                #aid��ȡʧ��
                return False
        else:
            #pse��ַ��ȡʧ��
            return False

        

    

    @staticmethod
    #pse �е� sfi��ȡ
    def psesfi(result):
        result = result[4:]
        #�ص�df����
        result = read_app.gettagvalue(result)
        result = result[4:]
        #�س�sfi
        result = read_app.gettagvalue(result)
        for i in range (10):
            if result == '9000'or result == '':
                break
            else:
                result = read_app.gettagvalue(result)
        if '88' in read_app.tag2value:
            data = '000' +  read_app.tag2value['88'] + '100'
            data = int(data,2)
            sfi = format(data,'x')
            if data < 16:
                sfi = '0' + sfi
            read_app.tag2value['88'] = sfi
            return True
        else:
            return False

    @staticmethod
    #����9f38��ֵ�������õ�pdol
    def process9f38(data):
        spdol = ''
        for i in range (12):
            tag = data[:2]
            if (tag == '5f') or (tag == '9f') or (tag == 'bf'):
                tag = data[:4]
                data = data[4:]
            else:
                data = data[2:]
            try:
                spdol = spdol + read_app.pdolvalue[tag]
            except Exception, e:
                raise e
            data = data[2:]
            if data == '':
                break
        return spdol
   

    @staticmethod
    #����ѡ��aid��Ƭ���ص�ֵ���������õ�pdol
    def pdol(data):
        data = data[4:]
        data = read_app.gettagvalue(data)
        data = data[4:]
        for i in range (10):
            if data == '9000' or data =='':
                break
            data = read_app.gettagvalue(data)
        if '9f38' in read_app.tag2value:
            pdollist = read_app.tag2value['9f38']
            spdol = read_app.process9f38(pdollist)
        return spdol
    
    @staticmethod
    #dataΪafl�ĵ�һ���ֽ�
    def sfidecode(data):
        num = int(data,16)
        binnum = bin(num)[:-3] + '100'
        num = int(binnum,2)
        sfi = format(num,'x')
        if num < 16:
            sfi = '0' +sfi
        return sfi

    @staticmethod
    def afl(data):
        character = data[4:8]
        read_app.tag2value['82'] = character
        data = data[8:]
        afl = data[:-4]
        #ÿ��afl��4�ֽ� sfi+first+last+static
        afllist = re.findall(r'(.{8})',afl)
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

    @staticmethod
    #����tag��ͷ�����ݷ��ؽض����ݣ�����һ��tag
    def gettagvalue(data):
        tag = data[:2]
        if (tag == '5f') or (tag == '9f') or (tag == 'bf'):
            tag = data[:4]
            data = data[4:]
        else:
            data = data[2:]
        slength = data[:2]
        length = int(slength,16)*2
        tagvalue = data[2:2+length]
        data = data[2+length:]
        read_app.tag2value[tag] = tagvalue
        if slength =='81':
            data = '81' + data
        return data
        
    
    #��֤data��9000��β
    @staticmethod
    def analyserecord(data):
        flag = 0
        first = data[:4]
        data = data[4:]
        if first != '7081':
            #��ͨ������
            for i in range(15):
                data = read_app.gettagvalue(data)
                if data == '9000' or data == '000':
                    break
        else:
            #��Կ�����ݻ�����00 B2 01 14 00���ص�����
            data = data[2:]
            for i in range(15):
                data = read_app.gettagvalue(data)
                if data[:2] == '81':
                    #����Կ������
                    break
                if data == '9000':
                    break
    @staticmethod
    def getdata(tag):
        data = APDU.getdata(tag)
        if data[-4:] =='9000':
            read_app.gettagvalue(data)
        else:
            pass

    @staticmethod
    def analysegac(data):
        tag  = data[:2] 
        if (tag == '80')and(data[-4:] == '9000') :
            slength = data[2:4]
            data = data[4:]
            data = data[:-4]
            read_app.tag2value['9f27'] = data[:2]
            read_app.tag2value['9f36'] = data[2:6]
            read_app.tag2value['9f26'] = data[6:22]
            read_app.tag2value['9f10'] = data[22:]
            return True
        else:
            return False



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
        pse_address = '315041592E5359532E4444463031'
        data = APDU.select(pse_address)
        read_app.pse(data)
        #print A6.CpuTransmit('00b2010c00')
        aid = read_app.aid(read_app.tag2value['88'])
        data = APDU.select(aid)
        spdolvalue = read_app.pdol(data)  
        data = APDU.gpo(spdolvalue)
        afllist = read_app.afl(data)
        for i in afllist:
            result = APDU.read_record(i)
            if result[-4:] == '9000':
                read_app.analyserecord(result)
            else:
                pass
        if '9f14' in read_app.tag2value:
            read_app.getdata('9f13')
        if '9f23' in read_app.tag2value:
            read_app.getdata('9f36')
        read_app.getdata('9f13')
        read_app.getdata('9f17')
        read_app.getdata('9f36')
        read_app.getcdol1()
        print read_app.cdol1
        print read_app.tag2value
       
    else:
        print('connect error')
    