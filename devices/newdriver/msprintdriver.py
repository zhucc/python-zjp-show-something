#!/usr/bin/python
# -*- coding: utf-8 -*-
#filename:msprintdriver.py; model:sp701
import serial
import binascii
import sys
from time import sleep
from ctypes import cdll
import re

'''
打印机操作类：
    openSerial() 打开串口，
    getdistance()获取超声波模块到纸卷的距离(mm),打不开so库会返回50
    recheckpaper()预缺纸检测，不缺纸返回True，缺纸返回False
    checkpaper() 缺纸检测,不缺纸返回True，缺纸返回False
    printmode()打印一个字符串,字符串必须是gbk格式的
    每行打印纸可以打印32个字符/字母/数字(len=32)或者16个汉字(len=48)
    bigger()增大接下来要打印的字体
    cancle_bigger()取消增大
    print_picture()打印下载进打印机的nv图
    
'''
class printdevice():
    distance = 40
    max_distance = 30
    baud_rate = 115200
    device_name = ""
    timeout = 1
    ser = None
    
    @staticmethod
    def com_detect():
        try:
            if printdevice.ser.isOpen():
                return True
        except Exception, e:
            if printdevice.opencom('/dev/ttyUSB0') == False:
                if printdevice.opencom('/dev/ttyUSB1') == False:
                    if printdevice.opencom('/dev/ttyUSB2') == False:
                        if printdevice.opencom('COM7') == False:
                            print('open com failed')
                            return False
            return printdevice.device_name

    @staticmethod
    def opencom(device_name):
        printdevice.device_name = device_name
        try:
            printdevice.ser = serial.Serial(printdevice.device_name,printdevice.baud_rate,timeout = printdevice.timeout)
            if printdevice.ser.isOpen():
                printdevice.ser.write( '100404'.decode('hex') )
                datarcv = printdevice.ser.readline()
                if datarcv:
                    return True
                else:
                    return False
            else:
                return False              
        except Exception, e:
            return False

        
    @staticmethod
    def getdistance():
        try:
            lib = cdll.LoadLibrary('./librecheck.so')
            lib.init()
        except Exception,e:
            return 50
        arr = []
        for i in range(4):
            data = lib.check()
            arr.append(data)
            sleep(0.01)
        arr.sort()
        brr = arr[1:3]
        sum = 0
        for i in brr:
            sum += i
        printdevice.distance = sum/len(brr)*17/100
        return printdevice.distance
    
    @staticmethod
    def recheckpaper():
        arr = []
        for i in range(4):
            data = printdevice.getdistance()
            arr.append(data)
            sleep(0.01)
        arr.sort()
        brr = arr[1:3]
        sum = 0
        for i in brr:
            sum += i
        printdevice.distance = sum/len(brr)
        if printdevice.distance >= printdevice.max_distance:
            return False
        else:
            return True
        
    @staticmethod
    def checkpaper():
        printdevice.ser.write( '100404'.decode('hex') )
        datarcv = printdevice.ser.readline()
        datarcv = binascii.b2a_hex(datarcv)
        if datarcv == '10':
            return True
        elif datarcv == '70':
            return False
        else:
            return True#其他情况也按照不缺纸的情况
    

        
    @staticmethod
    def printmode(string):
        printdevice.ser.write(string.decode('utf-8').encode('gbk'))
        printdevice.ser.write( '0A'.decode('hex') )

    @staticmethod
    def bigger():
        printdevice.ser.write( '1D2110'.decode('hex') ) #倍宽
        printdevice.ser.write( '1B4501'.decode('hex') ) #加粗
    
    @staticmethod
    def cancle_bigger():
        printdevice.ser.write( '1D2100'.decode('hex') )
        printdevice.ser.write( '1B4500'.decode('hex') )
    @staticmethod
    def print_picture():
         printdevice.ser.write( '1C700100'.decode('hex') )
    @staticmethod
    def print_string(strings = ""):
        printdevice.com_detect()
        printdevice.ser.isOpen()
        # printdevice.ser.write( '1D284102000002'.decode('hex'))
        # printdevice.print_picture()
        printdevice.printmode('********************************')
        printdevice.bigger()
        printdevice.printmode('           浙江省人民医院')
        # printdevice.printmode('')
        printdevice.printmode('             挂号凭条')
        printdevice.cancle_bigger()
        printdevice.printmode('')
        m = re.compile(r'\n').split(strings)
        for i,e in enumerate(m):
            m[i] = "  " + e + '\n'
        stringNew = "".join(m)
        printdevice.printmode(stringNew)
        printdevice.printmode('请妥善管理好您的凭条，以作为就诊凭证')
        # printdevice.printmode('凭证')
        printdevice.printmode('如需打印发票门诊大厅发票打印')
        printdevice.printmode('********************************')
        printdevice.printmode('')
        printdevice.printmode('')
        printdevice.printmode('')

if __name__ == "__main__":
    import ConfigParser
    import compro
    #init start
    compro.comprocess.allocatecom()
    #init end
    cf = ConfigParser.ConfigParser()
    cf.read('showsys.conf')
    device_name = cf.get('device','printer')
    
    if printdevice.opencom(device_name):
        #printdevice.ser.write( '1D284102000002'.decode('hex') ) #倍宽

       
        #每行打印纸可以打印32个字符/字母/数字(len=32)或者16个汉字(len=48)
        #printdevice.print_picture()
        printdevice.printmode('********************************')
        printdevice.bigger()
        printdevice.printmode('     青岛市妇幼儿童医院')
        printdevice.printmode('')
        printdevice.printmode('     门诊费用缴费凭条')
        printdevice.cancle_bigger()
        printdevice.printmode('')
        printdevice.printmode('  状态：     缴费成功')
        printdevice.printmode('  姓名：     赵日天')
        printdevice.printmode('  账户号：    999999')
        printdevice.printmode('  缴费方式：  预缴金')
        printdevice.printmode('  预缴款余额： 1000，000')
        printdevice.printmode('2015-10-19 15：30：00')
        printdevice.printmode('')
        printdevice.printmode('          收费项目明细')
        printdevice.printmode('  项目名称     金额')
        printdevice.printmode('  红牛         100')
        printdevice.printmode('  可乐         50')
        printdevice.printmode('  缴费总金额    150')
        printdevice.printmode('  操作员：      良辰    ')
        printdevice.printmode('********************************')
        printdevice.printmode('')
        printdevice.printmode('')
        printdevice.printmode('')
    else:
        print 'no com found' 




