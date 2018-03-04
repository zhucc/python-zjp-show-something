#!/usr/bin/python
# -*- coding: utf-8 -*-
#filename:ID_read.py
#model:维尔科技
import serial
import binascii
from multifunction_reader import reader
class ID():  
    '''
    name     名字
    gender   性别
    nation   民族
    birthday 出生日期
    address  住址
    identity 身份证号
    issuing_authority 签发机关
    begin_date 起始有效期限
    end_date   截止有效期限
    reserve    预留
    '''
    name = '1'
    gender = '1'
    nation = '1'
    birthday = '1'
    address = '1'
    identity = '1'
    issuing_authority = '1'
    begin_date = '1'
    end_date = '1'
    reserve = '1'
    #picture = ''
    nationlist = ['',
    '汉','蒙古','回','藏','维吾尔','苗','彝','壮','布依','朝鲜',
    '满','侗','瑶','白','土家','哈尼','哈萨克','傣','黎','傈僳',
    '佤','畲','高山','拉祜','水','东乡','纳西','景颇','柯尔克孜','土',
    '达斡尔','仫佬','羌','布朗','撒拉','毛南','仡佬','锡伯','阿昌','普米',
    '塔吉克','怒','乌孜别克','俄罗斯','鄂温克','德昂','保安','裕固','京','塔塔尔',
    '独龙','鄂伦春','赫哲','门巴','珞巴','基诺','','','','',
    '','','','','','','','','','',
    '','','','','','','','','','',
    '','','','','','','','','','',
    '','','','','95','96','其他','外国血统中国籍人士']
    genderlist = ['未知','男','女','3','4','5','6','7','8','未说明']

    #串口设置
    device_name = ''
    baud_rate = 115200
    timeout = 1
    ser = None
        
    @staticmethod
    def opencom(device_name):
        try:
            ID.device_name = device_name
            ID.ser = serial.Serial(ID.device_name,ID.baud_rate,timeout = ID.timeout)
            if ID.ser.isOpen():
                if ID.test_com() == True:
                    return True
                else:
                    return False
            else:
                return False
        except Exception, e:
            return False

    @staticmethod
    def com_detect():
        if ID.opencom('/dev/ttyUSB0') == False:
            if ID.opencom('/dev/ttyUSB1') == False:
                if ID.opencom('/dev/ttyUSB2') == False:
                    if ID.opencom('COM2') == False:
                        return False
        return True
         
    @staticmethod
    def clear_infomation():
        ID.name = ''
        ID.gender = ''
        ID.nation = ''
        ID.birthday = ''
        ID.address = ''
        ID.identity = ''
        ID.issuing_authority = ''
        ID.begin_date = ''
        ID.end_date = ''
        ID.reserve = ''
        #ID.picture = ''
    
    @staticmethod
    def check_recv_data(string):
        length = string[10:14]
        sw = string[14:20]
        crc = string[-2:]
        checkcrc = 0
        #计算校验和
        string = string[10:-2]
        for i in range(len(string)/2):
            firstbyte = string[0:2]
            string = string[2:]
            if (firstbyte != '00'):
                checkcrc = (int(firstbyte,16)) ^ checkcrc     
        if checkcrc == int(crc,16):
            return True
        else:
            return False
    @staticmethod
    def test_com():
        command = 'AAAAAA9669000311FFED'.decode('hex')
        try:
            ID.ser.write(command)
            datarcv = ID.ser.read(52)
            datarcv = binascii.b2a_hex(datarcv)
            if datarcv == 'aaaaaa9669000400009094':
                return True
            else:
                return False
        except Exception,e:
            return False

    @staticmethod                   
    def identity_read():
        #寻找卡片
        command1="AAAAAA96690003200122".decode("hex")
        #选择卡片
        command2="AAAAAA96690003200221".decode("hex")
        #读取卡片
        command3="AAAAAA96690003300132".decode("hex")
        try:
            ID.ser.write(command1)
            datarcv1 = ID.ser.read(52)
            datarcv1 = binascii.b2a_hex(datarcv1)
            #print 'datarcv1:',datarcv1
            if(datarcv1 == 'aaaaaa9669000800009f0000000097'):
                try:
                    ID.ser.write(command2)
                    datarcv2 = ID.ser.read(52)
                    datarcv2 = binascii.b2a_hex(datarcv2)
                    #print 'datarcv2:',datarcv2
                    if(datarcv2 == 'aaaaaa9669000c00009000000000000000009c'):
                        try:
                            ID.ser.write(command3)
                            data = ID.ser.read(1295)
                            #sw3=90代表操作成功
                            if((ID.check_recv_data(binascii.b2a_hex(data))) and ((binascii.b2a_hex(data[7:10]))=='000090')):
                                ID.name = data[14:44].decode("utf-16").encode("utf-8")

                                gendernum = data[44:46].decode("utf-16").encode("utf-8")
                                ID.gender = ID.genderlist[int(gendernum)]
                            
                                nationnum = data[46:50].decode("utf-16").encode("utf-8")
                                ID.nation = ID.nationlist[int(nationnum)]
                            
                                ID.birthday = data[50:66].decode("utf-16").encode("utf-8")
                                ID.address = data[66:136].decode("utf-16").encode("utf-8")
                                ID.identity = data[136:172].decode("utf-16").encode("utf-8")
                                ID.issuing_authority = data[172:202].decode("utf-16").encode("utf-8")
                                ID.begin_date = data[202:218].decode("utf-16").encode("utf-8")
                                ID.end_date = data[218:234].decode("utf-16").encode("utf-8")
                                ID.reserve = data[234:270].decode("utf-16").encode("utf-8")
                                #ID.picture = data[270:1295].decode("utf-16").encode("utf-8")
                                return True
                            else:
                                return False
                        except Exception,e:
                            return e
                    else:
                        return False
                except Exception,e:
                    return e                
            elif (datarcv1 == 'aaaaaa9669000400008084'):
                print 'no ID card!!'
            else:
                return False
        except Exception,e:
            return e

if __name__ == "__main__":
    if ID.com_detect():
        print 'connect success'
        print ID.identity_read()
        print(ID.name)
        print(ID.nation)
        print(ID.gender)
        print(ID.identity)
        ID.clear_infomation()
        print(ID.name)
        print(ID.nation)
        print(ID.gender)
        print(ID.identity)
    else:
        print 'connect error'
    
    
    

