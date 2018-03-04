# -*- coding: utf-8 -*-
import os
class ds1302():   
    def getdstime(self):
        '''
        根据ds1302时间设置系统时间
        '''
        os.system('sudo ./ds1302 -slc')
    def setdstime(self):
        '''
        根据系统时间设置ds1302时间
        '''
        os.system('sudo ./ds1302 -sdsc')
        
    def get_internet_time(self):
        '''
        根据网络时间设置系统时间
        '''
        os.system('ntpdate cn.pool.ntp.org')
        
    def manual_calibration(self,string1,string2):
        '''
        手动校准
        '''
        os.system('sudo date -s %s'%(string1))
        os.system('sudo date -s %s'%(string2))
        ds1302().setdstime()
        ds1302().getdstime()
        
    def auto_calibration(self):
        '''
        根据网络时间校准
        '''
        ds1302().get_internet_time()
        ds1302().setdstime()
        ds1302().getdstime()
        
if __name__=='__main__':
    
    #手动校准系统时间
    ds1302().manual_calibration('2015-10-20','11:28:00')
    '''
    #网络校准系统时间
    ds1302().auto_calibration()
    '''
