#!/usr/bin/python
# -*- coding: utf-8 -*-
#filename:ble.py
import serial
import binascii

class ble():

    baud_rate = 115200
    device_name = ''
    timeout = 0.3
    ser = None
    #馒头科技的at指令集
    ATcmd= { '版本查询':'AT+VERS?',
             '查询/设置——设备名':'AT+NAME',
             '恢复出厂设置':'AT+RENEW',
             '重启模块':'AT+RESET',
             '查询——当前工作状态':'AT+STAS?',
             '查询/设置——状态通知使能':'AT+NOTI',
             '查询/设置——模块工作方式':'AT+IMME',
             '查询/设置——主从模式':'AT+ROLE',
             '远控指令':'AT+R',

             '查询/设置——串口波特率':'AT+BAUD',
             '查询/设置——串口停止位':'AT+STOP',
             '查询/设置——串口发送延时时间':'AT+SDLY',

             '查询/设置——广播间隔':'AT+ADVI',
             '查询/设置——模块发射功率':'AT+POWE',
             '广播控制':'AT+ADST',

             '扫描从机':'AT+SCAN',
             '设置/查询——扫描参数':'AT+RANG',
             '连接搜索结果中指定序号的设备':'AT+CONN',
             '连接指定地址的设备':'AT+CON',
             '连接最后一次连接成功的设备':'AT+CONL',
             '断开当前连接':'AT+DISC',
             '查询——当前连接的设备地址':'AT+LADDR?',
             '读取 RSSI 信号强度':'AT+RSSI?',

             '查询/设置——LED 提示方式':'AT+LED',
             '查询/设置——单个 IO 电平':'AT+PIO',
             '查询/设置——多个 IO 电平':'AT+MPIO',
             '查询/设置——PWM 输出':'AT+PWM',
             '查询——ADC 当前电压':'AT+ADC?',

             '查询/设置——用户自定义数据':'AT+UADT',
             '查询/设置——本机 MAC 地址':'AT+MAC',
             '查询/设置——模块自动待机时间':'AT+LDLY',
             '查询/设置——传输速率':'AT+RATE',
             '使模块进入待机':'AT+SLEEP',
             '查询电量信息':'AT+BATT?'
             #'固件升级':'AT+UPDATE'
            }
    @staticmethod
    def opencom(device_name):
        try:
            ble.ser = serial.Serial(device_name,ble.baud_rate,timeout = ble.timeout)
            if ble.ser.isOpen():  
                if ble.com_comfirm():
                    return True
                else:
                    print'port'+device_name+'open fasle'
                    return False
            else:
                print ('port'+device_name+'open failed')
                return False
        except Exception, e:
            return False

    @staticmethod
    def com_detect():
        try:
            if ble.ser.isOpen():
                return True
        except Exception, e:
            if ble.opencom('/dev/ttyUSB0') == False:
                if ble.opencom('/dev/ttyUSB1') == False:
                    if ble.opencom('/dev/ttyUSB2') == False:
                        if ble.opencom('COM4') == False:
                            return False
            print('open com success')
            return True
     
    @staticmethod
    def com_comfirm(cmd = 'AT+'):
        ble.ser.write(cmd)
        rcvbuff = ble.ser.read(10)
        if rcvbuff == 'WAR+WAKE'or'OK+':
            return True
        else:
            return False 

    @staticmethod
    def cmd_process(cmd,parameter=''):
        cmd = ble.ATcmd[cmd]
        if parameter != '':
            if parameter == '?':
                cmd = cmd + parameter
            else:
                cmd = cmd + '['+ parameter + ']'
        print 'cmd:',cmd

        ble.ser.write(cmd)
        rcvbuff = ble.ser.read(200)
        if rcvbuff[:3] == 'OK+':
            print rcvbuff[3:]
            return rcvbuff[3:]
        elif rcvbuff == 'ERR+AT':
            print '指令错误'
            return False
        elif rcvbuff == 'ERR+PARA':
            print '参数错误'
            return False
        else:
            print 'data error:' + rcvbuff
            return False


                                                                          
                                            
if __name__ == '__main__':
    import time
    ble.com_detect()
    
    ble.cmd_process('版本查询')
    ble.cmd_process('查询/设置——设备名','?')
    ble.cmd_process('查询/设置——主从模式','P')
    ble.cmd_process('读取 RSSI 信号强度')
    #ble.cmd_process('查询/设置——设备名','laolihua')
    '''
    ble.cmd_process('恢复出厂设置')
    ble.cmd_process('重启模块')
    time.sleep(10)
    ble.cmd_process('查询——当前工作状态')
    ble.cmd_process('查询/设置——状态通知使能','?')
    ble.cmd_process('查询/设置——模块工作方式','?')
    ble.cmd_process('查询/设置——主从模式','C')
    ble.cmd_process('查询/设置——主从模式','?')
    ble.cmd_process('查询/设置——串口波特率','?')
    ble.cmd_process('查询/设置——串口停止位','?')
    ble.cmd_process('查询/设置——串口发送延时时间','?')
    
    #slave mode
    ble.cmd_process('查询/设置——广播间隔','?')
    ble.cmd_process('查询/设置——模块发射功率','?')
    ble.cmd_process('广播控制','Y')

    #master mode
   
    ble.cmd_process('扫描从机')
   
    ble.cmd_process('设置/查询——扫描参数','?')
    ble.cmd_process('连接搜索结果中指定序号的设备','?')
    ble.cmd_process('查询/设置——广播间隔','?')
    
    ble.cmd_process('断开当前连接')
    ble.cmd_process('查询——当前连接的设备地址')
    ble.cmd_process('读取 RSSI 信号强度')

    ble.cmd_process('查询/设置——LED 提示方式','?')
    #ble.cmd_process('查询/设置——单个 IO 电平','?')
    #ble.cmd_process('查询/设置——多个 IO 电平','?')
    #ble.cmd_process('查询/设置——PWM 输出','?')
    ble.cmd_process('查询——ADC 当前电压')

    ble.cmd_process('查询/设置——用户自定义数据','?')
    ble.cmd_process('查询/设置——本机 MAC 地址','?')
    ble.cmd_process('查询/设置——模块自动待机时间','?')
    ble.cmd_process('查询/设置——传输速率','?')
    ble.cmd_process('使模块进入待机')
    ble.cmd_process('查询电量信息')
    '''