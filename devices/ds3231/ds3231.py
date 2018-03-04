#!/usr/bin/python
# -*- coding: utf-8 -*-
#filename:ds3231.py
import wiringpi2 as wpi
class ds3231():
    '''
    时钟模块函数:
    check_connection()检查时钟模块是否正常连接.正常返回true，否则返回false

    set_date(name,data_name)data:值(int);data_name:值类型(string)- 
        year,month,date,day,hours,minutes,seconds.成功返回true,失败返回false
    set_alldate()一次设置所有的时间，格式为set_alldate(16,2,27,6,14,40,50),2016-2-27号，周六，14:40:50秒
        成功返回true,失败返回false
    readalldate()读取所有的时间，返回字典或false
    

    '''
    date_address = {'year':6,'month':5,'date':4,'day':3,'hours':2,'minutes':1,'seconds':0}
    
    ds = wpi.wiringPiI2CSetup(0x68)
    write = wpi.wiringPiI2CWriteReg8
    read = wpi.wiringPiI2CReadReg8
    
    @staticmethod
    def bcd2(bcd):
        try:
            return (bcd>>4)*10+(bcd&0xf)
        except Exception, e:
            print e
            return False

    @staticmethod    
    def s2bcd(s):
        try:
            result = (s/10)<<4 
            result = result + s%10
            return result
        except Exception, e:
            print e
            return False

    @staticmethod
    def checkdata(data,data_name):
        if isinstance(data,int)and isinstance(data_name,basestring):
            if data_name == 'year':
                if not((data>=0)and(data<=99)):
                    print data_name,':',data,'is out of range:0-99'
                    return False
            elif data_name == 'month':
                if not((data>=0)and(data<=12)):
                    print data_name,':',data,'is out of range:0-12'
                    return False
            elif data_name == 'day':
                if not((data>=0)and(data<=31)):
                    print data_name,':',data,'is out of range:0-31'
                    return False
            elif data_name == 'date':
                if not((data>=1)and(data<=7)):
                    print data_name,':',data,'is out of range:1-7'                
                    return False
            elif data_name == 'hours':
                if not((data>=0)and(data<=24)):
                    print data_name,':',data,'is out of range:0-24'
                    return False
            elif data_name == 'minutes':
                if not((data>=0)and(data<=60)):
                    print data_name,':',data,'is out of range:0-60'
                    return False
            elif data_name == 'seconds':
                if not((data>=0)and(data<=60)):
                    print data_name,':',data,'is out of range:0-60'
                    return False
            else:
                print 'data_name:',data_name,'error,','it must be one of these:year,month,date,day,hours,minutes,seconds' 
                return False
            return True
        else:
            print 'data format error,data is int and data_name is string'
    
    @staticmethod
    def check_connection():
        result = ds3231.readalldate()
        if result and (result == {'seconds': 5, 'month': 5, 'hours': 5, 'year': 5, 'date': 5, 'minutes': 5, 'day': 5}):
            print 'pi and ds3231 have been disconnected' 
            return False
        else:
            return True

    @staticmethod 
    def set_date(data,data_name):
        try:
            if ds3231.checkdata(data,data_name):
                ds3231.write(ds3231.ds,ds3231.date_address[data_name],ds3231.s2bcd(data))
                read_data = ds3231.bcd2(ds3231.read(ds3231.ds,ds3231.date_address[data_name]))
                if read_data and (read_data == data):
                    return True 
                else:
                    ds3231.check_connection()
                    return False
            else:
                return False
        except Exception, e:
            print e 
            return False
    
    @staticmethod
    def set_alldate(year,month,date,day,hours,minutes,seconds):
        try:
            ds3231.set_date(year)
            ds3231.set_date(month)
            ds3231.set_date(date)
            ds3231.set_date(day)
            ds3231.set_date(hours)
            ds3231.set_date(minutes)
            ds3231.set_date(seconds)
            #读取成功
            return True 
        except Exception, e:
            print e
            return False
            


    @staticmethod   
    def readalldate():
        try:
            date = {}
            date['seconds'] = ds3231.bcd2(ds3231.read(ds3231.ds,ds3231.date_address['seconds']))
            date['minutes'] = ds3231.bcd2(ds3231.read(ds3231.ds,ds3231.date_address['minutes']))
            date['hours'] = ds3231.bcd2(ds3231.read(ds3231.ds,ds3231.date_address['hours']))
            #week day
            date['day'] = ds3231.bcd2(ds3231.read(ds3231.ds,ds3231.date_address['day']))
            date['date'] = ds3231.bcd2(ds3231.read(ds3231.ds,ds3231.date_address['date']))
            date['month'] = ds3231.bcd2(ds3231.read(ds3231.ds,ds3231.date_address['month']))
            date['year'] = ds3231.bcd2(ds3231.read(ds3231.ds,ds3231.date_address['year']))
            return date
        except Exception, e:
            print e
            return False
            
    
if __name__ == '__main__':
    #ds3231.set_alldate(16,2,27,6,14,40,50)
    print ds3231.set_date(16,'year')
    import time
    while 1:
        result = ds3231.readalldate()
        #print result['year'],'年',result['month'],'月',result['date'],'日','周',result['day']
        print result['hours'],'时',result['minutes'],'分',result['seconds'],'秒'
        time.sleep(1)
    
