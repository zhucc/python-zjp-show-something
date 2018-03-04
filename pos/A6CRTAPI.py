#!/usr/bin/python
# -*- coding: utf-8 -*-
#filename:A6CRTAPI.py
from ctypes import *
import os
import re
_file = 'A6CRTAPI.dll'
_mod = WinDLL('A6CRTAPI.dll')

#LONG   WINAPI A6_Connect( __in DWORD dwPort, __in DWORD dwSpeed, __out PREADERHANDLE phReader ); 
_A6_Connect = _mod.A6_Connect
_A6_Connect.argtypes = (c_ulong,c_ulong,POINTER(c_long))
_A6_Connect.restype = c_long
#LONG   WINAPI A6_Disconnect( __in READERHANDLE hReader );

A6_Disconnect = _mod.A6_Disconnect
A6_Disconnect.argtypes = (c_long,)
A6_Disconnect.restype = c_long
#LONG   WINAPI A6_Initialize( __in READERHANDLE hReader,__in BYTE bResetMode,__out PBYTE pbVerBuff,__inout PDWORD pcbVerLength);
_A6_Initialize = _mod.A6_Initialize
_A6_Initialize.argtypes = (c_long,c_ubyte,POINTER(c_ubyte),POINTER(c_ulong))
_A6_Initialize.restype = c_long
#LONG   WINAPI A6_SetCardIn( __in READERHANDLE hReader,__in BYTE bFrontSet,__in BYTE bRearSet);
_A6_SetCardIn = _mod.A6_SetCardIn
_A6_SetCardIn.argtypes = (c_long,c_ubyte,c_ubyte)
_A6_SetCardIn.restype = c_long
#LONG   WINAPI A6_SetDockedPos( __in READERHANDLE hReader,__in BYTE bDockedPos);
_A6_SetDockedPos = _mod.A6_SetDockedPos
_A6_SetDockedPos.argtypes = (c_long,c_ubyte)
_A6_SetDockedPos.restype = c_long
#LONG   WINAPI A6_SetBaudRate( __in READERHANDLE hReader, __in DWORD dwBaudRate );
_A6_SetBaudRate = _mod.A6_SetBaudRate
_A6_SetBaudRate.argtypes = (c_long,c_ulong)
_A6_SetBaudRate.restype = c_long
#LONG   WINAPI A6_GetCRCondition( __in READERHANDLE hReader,__out PCRSTATUS pStatus);
_A6_GetCRCondition = _mod.A6_GetCRCondition
_A6_GetCRCondition.argtypes = (c_long,c_ubyte,POINTER(c_ubyte),POINTER(c_ulong))       #to do
_A6_GetCRCondition.restype = c_long
#LONG   WINAPI A6_DetectIccType( __in READERHANDLE hReader, __out PBYTE pbType );
_A6_DetectIccType = _mod.A6_DetectIccType
_A6_DetectIccType.argtypes = (c_long,POINTER(c_ubyte))
_A6_DetectIccType.restype = c_long
#LONG   WINAPI A6_MoveCard( __in READERHANDLE hReader,__in BYTE bMoveMethod);
_A6_MoveCard = _mod.A6_MoveCard
_A6_MoveCard.argtypes = (c_long,c_ubyte)
_A6_MoveCard.restype = c_long
#LONG   WINAPI A6_LedOn( __in READERHANDLE hReader );
_A6_LedOn = _mod.A6_LedOn
_A6_LedOn.argtypes = (c_long,)
_A6_LedOn.restype = c_long 
#LONG   WINAPI A6_LedOff( __in READERHANDLE hReader );
_A6_LedOff = _mod.A6_LedOff
_A6_LedOff.argtypes = (c_long,)
_A6_LedOff.restype = c_long
#LONG   WINAPI A6_LedBlink( __in READERHANDLE hReader,__in BYTE bOnTime,__in BYTE bOffTime);
_A6_LedBlink = _mod.A6_LedBlink
_A6_LedBlink.argtypes = (c_long,c_ubyte,c_ubyte)
_A6_LedBlink.restype = c_long
#LONG   WINAPI A6_IccPowerOn( __in READERHANDLE hReader );
_A6_IccPowerOn = _mod.A6_IccPowerOn
_A6_IccPowerOn.argtypes = (c_long,)
_A6_IccPowerOn.restype = c_long
#LONG   WINAPI A6_IccPowerOff( __in READERHANDLE hReader );
_A6_IccPowerOff = _mod.A6_IccPowerOff
_A6_IccPowerOff.argtypes = (c_long,)
_A6_IccPowerOff.restype = c_long


"""SAM"""

#LONG   WINAPI A6_SamActivate( __in READERHANDLE hReader, __in BYTE bSAMNumber, __in BYTE bVoltage, 
#__out PBYTE pbATRBuff, __inout PDWORD pcbATRLength);
_A6_SamActivate = _mod.A6_SamActivate
_A6_SamActivate.argtypes = (c_long,c_ubyte,c_ubyte,POINTER(c_ubyte),POINTER(c_ulong))
_A6_SamActivate.restype = c_long
#LONG   WINAPI A6_SamDeactivate( __in READERHANDLE hReader );
_A6_SamDeactivate = _mod.A6_SamDeactivate
_A6_SamDeactivate.argtypes = (c_long,)
_A6_SamDeactivate.restype = c_long
#LONG   WINAPI A6_SamTransmit( __in READERHANDLE hReader, __in BYTE bProtocol,__in BYTE bSAMNumber, 
#__in PBYTE pbSendBuff, __in USHORT cbSendLength, __out PBYTE pbRecvBuff, __inout PDWORD pcbRecvLength );
_A6_SamTransmit = _mod.A6_SamTransmit
_A6_SamTransmit.argtypes = (c_long,c_ubyte,c_ubyte,POINTER(c_ubyte),c_ushort,POINTER(c_ubyte),POINTER(c_ulong))
_A6_SamTransmit.restype = c_long

"""ic"""

#LONG   WINAPI A6_CpuColdReset( __in READERHANDLE hReader, __out PBYTE pbATRBuff, __inout PDWORD pcbATRLength );
_A6_CpuColdReset = _mod.A6_CpuColdReset
_A6_CpuColdReset.argtypes = (c_long,POINTER(c_ubyte),POINTER(c_ulong))
_A6_CpuColdReset.restype = c_long
#LONG   WINAPI A6_CpuWarmReset( __in READERHANDLE hReader, __out PBYTE pbATRBuff, __inout PDWORD pcbATRLength );
_A6_CpuWarmReset = _mod.A6_CpuWarmReset
_A6_CpuWarmReset.argtypes = (c_long,POINTER(c_ubyte),POINTER(c_ulong))
_A6_CpuWarmReset.restype = c_long
#LONG   WINAPI A6_CpuTransmit( __in READERHANDLE hReader, __in BYTE bProtocol,__in PBYTE pbSendBuff, 
#__in USHORT cbSendLength, __out PBYTE pbRecvBuff, __inout PDWORD pcbRecvLength );
_A6_CpuTransmit = _mod.A6_CpuTransmit
_A6_CpuTransmit.argtypes = (c_long,c_ubyte,POINTER(c_ubyte),c_ushort,POINTER(c_ubyte),POINTER(c_ulong))
_A6_CpuTransmit.restype = c_long

class A6():
    hReader = 0
    Protocol = 1
    @staticmethod
    def Connect(port,speed):
        phReader = c_long()
        result =_A6_Connect(port,speed,phReader)
        A6.hReader = phReader.value 
        return result,phReader.value
    
    @staticmethod
    def Initialize(ResetMode = 0x30):
        '''
        RESET_ONLY          0x30
        RESET_AND_EJECT     0x31
        RESET_AND_CAPTURE   0x32
        '''
        VerBuff = c_ubyte()
        VerLength = c_ulong()
        result = _A6_Initialize(A6.hReader,ResetMode,VerBuff,VerLength)
        return result,VerBuff.value,VerLength.value

    @staticmethod
    def SetCardIn(FCI = 0x33,RCI = 0x31):
        '''
        FCI_PROHIBITED      0x31
        FCI_MAGCARD_ONLY    0x32
        FCI_ALLOWED         0x33

        RCI_ALLOWED         0x30
        RCI_PROHIBITED      0x31
        '''
        result = _A6_SetCardIn(A6.hReader,FCI,RCI)
        return result

    @staticmethod
    def SetDockedPos(DPOS = 0x33):
        '''
        DPOS_FRONT_NH   0x30
        DPOS_FRONT      0x31
        DPOS_INTERNAL   0x32
        DPOS_IC_POS     0x33
        DPOS_REAR       0x34
        DPOS_REAR_NH    0x35
        '''
        result = _A6_SetDockedPos(A6.hReader,DPOS)
        return result
    
    def SetBaudRate(BaudRate = 9600):
        result = _A6_SetBaudRate(A6.hReader,BaudRate)
        return result

    @staticmethod
    def DetectIccType():
        '''
        ICCTYPE_UNKNOWN     0x0
        ICCTYPE_MIFARE_S50  0x10
        ICCTYPE_MIFARE_S70  0x11
        ICCTYPE_MIFARE_UL   0x12
        ICCTYPE_TYPEA_CPU   0x13
        ICCTYPE_TYPEB_CPU   0x14
        ICCTYPE_T0_CPU      0x20
        ICCTYPE_T1_CPU      0x21
        ICCTYPE_AT24C01     0x30
        ICCTYPE_AT24C02     0x31
        ICCTYPE_AT24C04     0x32
        ICCTYPE_AT24C08     0x33
        ICCTYPE_AT24C16     0x34
        ICCTYPE_AT24C32     0x35
        ICCTYPE_AT24C64     0x36
        ICCTYPE_SLE4442     0x40
        ICCTYPE_SLE4428     0x41
        ICCTYPE_AT88SC102   0x50
        ICCTYPE_AT88SC1604  0x51
        ICCTYPE_AT88SC1608  0x52
        ICCTYPE_AT45DB041   0x53
        '''
        cardType = c_ubyte()
        result = _A6_DetectIccType(A6.hReader,cardType)
        #print (cardType.value)
        if cardType.value is 32:
            A6.Protocol = 0x31 
        if cardType.value is 33:
            A6.Protocol = 0x32
        return result,cardType.value

    @staticmethod
    def MoveCard(MoveMethod=0x30):
        '''
        MOVE_TO_FRONT_NH    0x30
        MOVE_TO_FRONT       0x31
        MOVE_TO_RF_POS      0x2E
        MOVE_TO_IC_POS      0x2F
        MOVE_TO_REAR        0x32
        MOVE_TO_REAR_NH     0x33
        '''
        result = _A6_MoveCard(A6.hReader,MoveMethod)
        return result
    
    @staticmethod
    def LedOn():
        result = _A6_LedOn(A6.hReader)
        return result

    @staticmethod
    def LedOff():
        result = _A6_LedOff(A6.hReader)
        return result
        
    @staticmethod
    def LedBlink(OnTime = 8,OffTime = 8):
        result = _A6_LedBlink(A6.hReader,OnTime,OffTime)
        return result
    
    @staticmethod
    def IccPowerOn():
        result = _A6_IccPowerOn(A6.hReader)
        return result

    @staticmethod
    def IccPowerOff():
        result = _A6_IccPowerOff(A6.hReader)
        return result   
    """
    #SAM
    @staticmethod
    def SamActivate(SAMNumber = 0,Voltage = 0x2F):
        '''
        VOLTAGE_1_8     0x2E
        VOLTAGE_3       0x2F
        VOLTAGE_5       0x30
        '''
        ATRBuff = c_ubyte(99)
        ATRLength = c_ulong()
        result = _A6_SamActivate(A6.hReader,SAMNumber,Voltage,ATRBuff,ATRLength)
        return result,ATRBuff,ATRLength

    @staticmethod
    def SamDeactivate():
        result =_A6_SamDeactivate(A6.hReader)
        return result

    @staticmethod
    def SamTransmit(SAMNumber,SendBuff,SendLength,bProtocol):
        RecvBuff = (c_ubyte*300)()
        RecvLength = c_ulong(300)
        result = _A6_SamTransmit(A6.hReader,bProtocol,SAMNumber,SendBuff,SendLength,RecvBuff,RecvLength)
        buff = ''
        for i in range (RecvLength.value):
            buff = buff + format(RecvBuff[i],'x')
        return result,buff,RecvLength
    """
    #CPU
    @staticmethod
    def CpuColdReset():
        ATRBuff = (c_ubyte*20)()
        ATRLength = c_ulong(20)
        result = _A6_CpuColdReset(A6.hReader,ATRBuff,ATRLength)
        buff = ''
        for i in range (ATRLength.value):
            buff = buff + format(ATRBuff[i],'x')
        return result,buff,ATRLength.value

    @staticmethod
    def CpuWarmReset():
        ATRBuff = (c_ubyte*20)()
        ATRLength = c_ulong(20)
        result = _A6_CpuWarmReset(A6.hReader,ATRBuff,ATRLength)
        buff = ''
        for i in range (ATRLength.value):
            buff = buff + format(ATRBuff[i],'x')
        return result,buff,ATRLength.value

    @staticmethod
    def CpuTransmit(cmd):
        print cmd
        SendLength = len(cmd)/2
        SendBuff = A6.cmd2sendbuff(cmd)
        RecvBuff = (c_ubyte*500)()
        RecvLength = c_ulong(500)
        result = _A6_CpuTransmit(A6.hReader,A6.Protocol,SendBuff,SendLength,RecvBuff,RecvLength)
        if result is 0:
            buff = ''
            for i in range (RecvLength.value):
                string = format(RecvBuff[i],'x')
                if RecvBuff[i] < 16:
                    string = '0' + string
                buff = buff + string
            print buff
            return buff
        else:
            print result
            return result

    @staticmethod
    def cmd2sendbuff(cmd):
        strlist = re.findall(r'(.{2})',cmd)
        length = len(strlist)
        SendBuff = (c_ubyte*(length))()
        for i in range (length):
            SendBuff[i] = c_ubyte(int(strlist[i],16))
        return SendBuff


        pass
if __name__ == '__main__':
    connect_result = A6.Connect(2,9600)
    if  connect_result[0] is 0:
        hReader = connect_result[1]
        #A6_LedOn(hReader)
        print (A6.LedBlink(10,30))
        print (A6.SetCardIn())
        print (A6.SetDockedPos())
        #print (A6.MoveCard()) 
        print (A6.IccPowerOn())
        A6.DetectIccType()
        print (A6.CpuColdReset())
        print (A6.CpuWarmReset())
        cmd = '00A404000E315041592E5359532E4444463031'
        print (A6.CpuTransmit(cmd))
        cmd = '00b2010c00'
        print (A6.CpuTransmit(cmd))
    else:
        print('connect error')


    