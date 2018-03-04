#!/usr/bin/python
# -*- coding: utf-8 -*-
#filename:multifunction_reader.py
# model:华大集成三合一读卡器
# usage：
'''
所有返回数据，输入数据都为字符串
接触cpu:
1.cpu_coldreset()或者cpu_warmreset() out：true，false
2.cpu_apdu('00A404000e315041592E5359532E444446303100')in：apdu命令 out：磁道信息或者False
具体参考apdu命令集
3.cpu_poweroff() out：true，false
cpu_cardstatus() out：有卡未上电:03，
                      无卡:02，
                      有卡已上电:00，
                      或者False

磁条卡：
1.magcard('02')  in：磁道号 out：磁道信息或者False

取消读磁条卡
2.magcard_overtime('02') in：磁道号，out：true，false

m1卡：
m1_find():out:卡号

get_version()：获取读卡器版本号 ，用于检测串口号
'''
import serial
import re
import binascii
import time
import debug
import logging
logger = logging.getLogger('pos.log')

class reader():

    baud_rate = 115200
    device_name = ''
    timeout = 1
    ser = None
    #卡座号
    number = '0c'

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

    @staticmethod
    def opencom(device_name):
        try:
            reader.ser = serial.Serial(device_name,reader.baud_rate,timeout = reader.timeout)
            if reader.ser.isOpen():
                if reader.get_version():
                    reader.device_name = device_name
                    logger.info('open right com:' + reader.device_name)
                    return True
                else:
                    return False
            else:
                return False
        except Exception, e:
            return False

    @staticmethod
    def com_detect():
        try:
            if reader.ser.isOpen():
                return True
        except Exception, e:
            if reader.opencom('/dev/ttyUSB0') == False:
                if reader.opencom('/dev/ttyUSB1') == False:
                    if reader.opencom('/dev/ttyUSB2') == False:
                        if reader.opencom('COM6') == False:
                            logger.error('open com failed')
                            return False
            return True


    @staticmethod
    def _getlength(data):
        length = (len(data)+1)/2 + 4
        slength = format(length,'x')
        num = len(slength)
        if num < 4:
            slength = '0'*(4 - num) + slength
        hbyte = slength[:2]
        lbyte = slength[-2:]
        slength = lbyte + hbyte
        return slength

    @staticmethod
    def _crc(data):
        num = (len(data)+1)/2
        crcnum = 0
        for i in range(num):
            try:
                num = int(data[:2],16)
                crcnum = crcnum ^ num
                data = data[2:]
            except Exception, e:
                return 'error of change2int '
        crcstr = format(crcnum,'x')
        num = len(crcstr)
        if num < 2:
            crcstr = '0'*(2-num) + crcstr
        return crcstr

    @staticmethod
    #传入卡片返回的数据（字符串），crc校验后，返回状态和数据域
    def _analyse(data):
        data = data[8:-2]
        crcstr = data[-2:]
        #lenstr = data[2:4] + data[:2]
        statu = data[4:6]
        data = data[:-2]
        message = data[6:]
        crcresult = reader._crc(data)
        if crcresult == crcstr:
            lista = []
            lista.append(statu)
            lista.append(message)
            return lista
        else:
            logger.error(' rcv data crc error' + 'rcv:'+crcstr + 'calculator:'+crcresult)
            return ['01']

    @staticmethod
    def _cmd2return(data):
        cmd = data.decode('hex')
        reader.ser.write(cmd)
        rcvbuff = reader.ser.read(1023)
        rcvstr  = binascii.b2a_hex(rcvbuff)
        #print 'recive:',rcvstr[14:-4]
        # cx print 'reciveall',rcvstr
        resultlist = reader._analyse(rcvstr)
        return resultlist

    @staticmethod
    #读卡返回字典：键值有：'姓名'，'性别'，'国家'，'生日'，'地址'，
    #'身份证号'，'签发机关'，'起始日期'，'结束日期'，'预留'
    def readid():
        id_dict = {}
        cmd = 'fafbfcfd0400a4a0bb'
        resultlist = reader._cmd2return(cmd)
        if resultlist[0] == '00':
            cmd = 'fafbfcfd0400b0b4bb'
            resultlist = reader._cmd2return(cmd)
            if resultlist[0] == '00':
                cmd = 'fafbfcfd0400b1b5bb'
                resultlist = reader._cmd2return(cmd)
                if resultlist[0] == '00':
                    cmd = 'fafbfcfd0400b4b0bb'
                    cmd = cmd.decode('hex')
                    reader.ser.write(cmd)
                    rcvbuff = reader.ser.read(1023)
                    if binascii.b2a_hex(rcvbuff[6:7]) == '00':
                        idtext = rcvbuff[7:263]
                        name = idtext[0:30].decode("utf-16").encode("utf-8")
                        id_dict['姓名'] = name
                        gendernum = idtext[30:32].decode("utf-16").encode("utf-8")
                        id_dict['性别'] = reader.genderlist[int(gendernum)]

                        nationnum = idtext[32:36].decode("utf-16").encode("utf-8")
                        id_dict['国家'] = reader.nationlist[int(nationnum)]

                        id_dict['生日'] = idtext[36:52].decode("utf-16").encode("utf-8")

                        id_dict['地址'] = idtext[52:122].decode("utf-16").encode("utf-8")
                        id_dict['身份证号'] = idtext[122:158].decode("utf-16").encode("utf-8")
                        id_dict['签发机关'] = idtext[158:188].decode("utf-16").encode("utf-8")
                        id_dict['起始日期'] = idtext[188:204].decode("utf-16").encode("utf-8")
                        id_dict['结束日期'] = idtext[204:220].decode("utf-16").encode("utf-8")
                        id_dict['预留'] = idtext[220:256].decode("utf-16").encode("utf-8")
                        return id_dict
                    else:
                        return False
                else:
                    return False
            else:
                return False
        else:
            return False


    @staticmethod
    def get_version():
        slength = reader._getlength('')
        data = slength + 'a1'
        crcstr = reader._crc(data)
        data = 'fafbfcfd'+ data + crcstr + 'bb'
        resultlist = reader._cmd2return(data)
        if resultlist[0] == '00':
            return True
        else:
            return False

    #磁条卡
    @staticmethod
    def magcard(number,timetick = 10):
        slength = reader._getlength(number)
        data = slength + '70' + number
        crcstr = reader._crc(data)
        data = 'fafbfcfd'+ data + crcstr + 'bb'
        cmd = data.decode('hex')
        reader.ser.write(cmd)
        rcvbuff = ''
        start = time.time()
        while rcvbuff == '':
            rcvbuff = reader.ser.readline()
            end = time.time()
            if end - start > timetick:
                reader.magcard_overtime('02')
                break
        rcvstr  = binascii.b2a_hex(rcvbuff)
        resultlist = reader._analyse(rcvstr)
        if resultlist[0] == '00':
            return resultlist[1]
        else:
            return False

    @staticmethod
    def magcard_overtime(number = '02'):
        slength = reader._getlength(number)
        data = slength + '7b' + number
        crcstr = reader._crc(data)
        data = 'fafbfcfd'+ data + crcstr + 'bb'

        resultlist = reader._cmd2return(data)
        if resultlist[0] == '00':
            return True
        else:
            return False


    #接触式cpu卡
    @staticmethod
    def cpu_coldreset():
        number=reader.number
        slength = reader._getlength(number)
        data = slength + '74' + number
        crcstr = reader._crc(data)
        data = 'fafbfcfd'+ data + crcstr + 'bb'

        resultlist = reader._cmd2return(data)
        if resultlist[0] == '00':
            return True
        else:
            return False

    @staticmethod
    def cpu_warmreset():
        number=reader.number
        slength = reader._getlength(number)
        data = slength + '75' + number
        crcstr = reader._crc(data)
        data = 'fafbfcfd'+ data + crcstr + 'bb'

        resultlist = reader._cmd2return(data)
        if resultlist[0] == '00':
            return True
        else:
            return False

    @staticmethod
    def cpu_poweroff():
        number=reader.number
        slength = reader._getlength(number)
        data = slength + '73' + number
        crcstr = reader._crc(data)
        data = 'fafbfcfd'+ data + crcstr + 'bb'

        resultlist = reader._cmd2return(data)
        if resultlist[0] == '00':
            return True
        else:
            return False

    @staticmethod
    def cpu_apdu(apdudata):
        number=reader.number
        slength = reader._getlength(number + apdudata)
        data = slength + '72' + number + apdudata
        crcstr = reader._crc(data)
        data = 'fafbfcfd'+ data + crcstr + 'bb'

        resultlist = reader._cmd2return(data)
        if resultlist[0] == '00':
            return resultlist[1]
        else:
            logger.error('reader communication error')
            return False


    @staticmethod
    def cpu_cardstatus():
        number=reader.number
        slength = reader._getlength(number)
        data = slength + '77' + number
        crcstr = reader._crc(data)
        data = 'fafbfcfd'+ data + crcstr + 'bb'

        resultlist = reader._cmd2return(data)
        if resultlist[0] == '00' or resultlist[0] == '02' or resultlist[0] == '03':
            return resultlist[0]
        else:
            return False

    @staticmethod
    def cpu_readid():
        #读取杭州市民卡卡号
        print reader.cpu_coldreset()
        print reader.cpu_apdu('00A404000f7378312E73682EC9E7BBE1B1A3D5CF00')
        print reader.cpu_apdu('00A4000002ef06')
        data = reader.cpu_apdu('00B2080018')
        if data:
            data = data[4:-4]
            data = reader.combinecmd(data)
            reader.cpu_poweroff()
            return data
        else:
            return False
    @staticmethod
    def combinecmd(str1):
        strlist = re.findall(r'(.{2})',str1)
        s_combinecmd = ''
        for i in strlist:
            num = int(i)
            if num < 40:
                i = hex(num - 30)[2:]
            else:
                i = hex(num - 31)[2:]
            s_combinecmd = s_combinecmd + i
        return s_combinecmd


    #非接触式cpu卡
    @staticmethod
    def typeA_poweron():
        slength = '0400'
        data = slength + '20'
        crcstr = reader._crc(data)
        data = 'fafbfcfd'+ data + crcstr + 'bb'

        resultlist = reader._cmd2return(data)
        if resultlist[0] == '00':
            return True
        else:
            return False

    @staticmethod
    def typeB_poweron():
        slength = '0400'
        data = slength + '21'
        crcstr = reader._crc(data)
        data = 'fafbfcfd'+ data + crcstr + 'bb'

        resultlist = reader._cmd2return(data)
        if resultlist[0] == '00':
            return True
        else:
            return False

    @staticmethod
    def nonconnect_apdu(apdudata):
        slength = reader._getlength(apdudata)
        data = slength + '22' + apdudata
        crcstr = reader._crc(data)
        data = 'fafbfcfd'+ data + crcstr + 'bb'

        resultlist = reader._cmd2return(data)
        if resultlist[0] == '00':
            return resultlist[1]
        else:
            return False

    #m1卡号
    @staticmethod
    def m1_find():
        data = 'fafbfcfd0400292dbb'

        resultlist = reader._cmd2return(data)
        if resultlist[0] == '00':
            return resultlist[1]
        else:
            return False
    '''
    @staticmethod
    def _m1_read(block_address):
        slength = reader._getlength(block_address)
        data = slength + '24' + block_address
        crcstr = reader._crc(data)
        data = 'fafbfcfd'+ data + crcstr + 'bb'

        cmd = data.decode('hex')
        reader.ser.write(cmd)
        rcvbuff = reader.ser.read(500)
        rcvstr  = binascii.b2a_hex(rcvbuff)
        resultlist = reader._analyse(rcvstr)

        if resultlist[0] == '00':
            return resultlist[1]
        else:
            return False

    @staticmethod
    def m1_read(block_address):
        num = int(block_address,16)
        sec_nr = format((num/4),'x')
        if len(sec_nr) < 2:
            sec_nr = '0' + sec_nr
        if reader.m1_auth(sec_nr):
            result = reader._m1_read(block_address)
            if result == False:
                return False
            else:
                return result
        else:
            return False


    @staticmethod
    def m1_write(block_address,block_data):
        if len(block_data) == 32:
            slength = reader._getlength(block_address + block_data)
            data = slength + '25' + block_address + block_data
            crcstr = reader._crc(data)
            data = 'fafbfcfd'+ data + crcstr + 'bb'

            resultlist = reader._cmd2return(data)
            if resultlist[0] == '00':
                return True
            else:
                return False
        else:
            return False


    @staticmethod
    def _m1_incval(block_address,increasevalue):
        slength = reader._getlength(block_address + increasevalue)
        data = slength + '26' + block_address + increasevalue
        crcstr = reader._crc(data)
        data = 'fafbfcfd'+ data + crcstr + 'bb'

        resultlist = reader._cmd2return(data)
        print resultlist
        if resultlist[0] == '00':
            return True
        else:
            return False

    @staticmethod
    def m1_incval(block_address,increasevalue):
        num = int(block_address,16)
        sec_nr = format((num/4),'x')
        if len(sec_nr) < 2:
            sec_nr = '0' + sec_nr
        if reader.m1_auth(sec_nr):
            print 'auth success'
            result = reader._m1_incval(block_address,increasevalue)
            print result
            if result == False:
                return False
            else:
                return result
        else:
            return False

    @staticmethod
    def _m1_decval(block_address,decreasevalue):
        slength = reader._getlength(block_address + decreasevalue)
        data = slength + '27' + block_address + decreasevalue
        crcstr = reader._crc(data)
        data = 'fafbfcfd'+ data + crcstr + 'bb'

        resultlist = reader._cmd2return(data)
        if resultlist[0] == '00':
            return True
        else:
            return False

    @staticmethod
    def m1_decval(block_address,increasevalue):
        num = int(block_address,16)
        sec_nr = format((num/4),'x')
        if len(sec_nr) < 2:
            sec_nr = '0' + sec_nr
        if reader.m1_auth(sec_nr):
            result = reader._m1_decval(block_address,increasevalue)
            if result == False:
                return False
            else:
                return result
        else:
            return False

    @staticmethod
    def m1_loadkey(keymode,key):
        slength = reader._getlength(keymode + key)
        data = slength + '28' + keymode + key
        crcstr = reader._crc(data)
        data = 'fafbfcfd'+ data + crcstr + 'bb'

        resultlist = reader._cmd2return(data)
        if resultlist[0] == '00':
            return True
        else:
            return False
    '''

if __name__ == '__main__':
    import time
    if reader.com_detect():
        '''
        #接触cpu
        print reader.cpu_coldreset()
        print reader.cpu_warmreset()
        print reader.cpu_apdu('00A404000e315041592E5359532E444446303100')
        print reader.cpu_poweroff()
        print reader.cpu_cardstatus()
        #磁条卡
        print reader.magcard('02')
        print reader.magcard_overtime('02')
        '''
        def getm1_in30s():
            start = time.time()
            end = time.time()
            while (end - start < 30):
                temp = reader.m1_find()
                if temp:
                    print temp
                    break
                else:
                    end = time.time()
                    print 'waitting for m1....'

        def getid_in30s():
            start = time.time()
            end = time.time()
            while (end - start < 30):
                result = reader.readid()
                if result:
                    for key,value in result.items():
                        print key,':',value
                    break
                else:
                    end = time.time()
                    print 'waitting for idcard....'
        print reader.cpu_readid()
        #getid_in30s()
        #getm1_in30s()
        #getid_in30s()





    else:
        print 'no com found'
