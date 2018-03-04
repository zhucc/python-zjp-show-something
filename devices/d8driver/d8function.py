import serial
import binascii
#setdata
#setdata() out:string "02000580011122338603" in:num 0x8001112233 or string"0x8001112233"

def setdata(xdata):
    str_begin = "02"
    str_end = "03"
    #xdata = 0x80011122334455667
    if not(isinstance(xdata,str)):
        xdata = hex(xdata)
    #print(len(xdata))
    #print(isinstance(xdata,str))
    #print(xdata)
    xdatalen_d = int( (len(xdata)-1)/2 )
    xdatalen_h = hex(xdatalen_d)
    templen = len(xdatalen_h)
    if templen == 3:
        xdatalenHH = "0"
        xdatalenHL = "0"
        xdatalenLH = "0"
        xdatalenLL = xdatalen_h[-1]
    elif templen == 4:
        xdatalenHH = "0"
        xdatalenHL = "0"
        xdatalenLH = xdatalen_h[-2]
        xdatalenLL = xdatalen_h[-1]        
    elif templen == 5:
        xdatalenHH = "0"
        xdatalenHL = xdatalen_h[-3] 
        xdatalenLH = xdatalen_h[-2]
        xdatalenLL = xdatalen_h[-1]         
    elif templen == 6:
        xdatalenHH = xdatalen_h[-4] 
        xdatalenHL = xdatalen_h[-3] 
        xdatalenLH = xdatalen_h[-2]
        xdatalenLL = xdatalen_h[-1]        
    else:
        print ('error_datalen')
   #print (xdatalen_h)    
    #get data
    str_datalist=[]
    xdata= xdata[2:]
    if len(xdata)%2 != 0:
        xdata = "0"+xdata
    templen1 = int(len(xdata)/2)
    for i in range (templen1)[::1]:
        str_datalist.append(xdata[i*2:i*2+2])
    #print (xdata)
    #print (str_datalist)
    #get xor
    xdatalenH = xdatalenHH+xdatalenHL
    xdatalenL = xdatalenLH+xdatalenLL
    xdatalenH = int(xdatalenH,16)
    xdatalenL = int(xdatalenL,16)
    xornum = (int(str_begin,16))^xdatalenH
    xornum = xornum ^ xdatalenL
    num_datalist=[]
    for i in range (xdatalen_d):   
        num_datalist.append(int(str_datalist[i],16))
        xornum = xornum ^ num_datalist[i]
    xornum = hex(xornum)
    xornum = xornum[2:]
    #print(xornum)
    stringsend =str_begin + xdatalenHH + xdatalenHL + xdatalenLH + xdatalenLL
    #print(stringsend)
    for i in range (xdatalen_d):
        stringsend = stringsend + str_datalist[i]
    #print(stringsend)
    stringsend = stringsend + xornum
    stringsend = stringsend + str_end
    #print(stringsend)
    return stringsend



#checkdata
#checkdata() out: success: 1 fail: 0  in: string like: "02000580011122338603"

def checkdata(strxdata):
    #success:return 1 fail:return 0 in parameter:string like: "02000580011122338603"
    #strxdata = "02000580011122338603"
    #strxdata = str(xdata)
    if not(isinstance(strxdata,str)):
        datarcv = str(strxdata)
    strbegin = strxdata[:2]
    strdatalen = strxdata[2:6]
    strend = strxdata[-2:]
    strxor = strxdata[-4:-2]
    strxdata = strxdata[6:]
    strxdata = strxdata[:-4]
    strcmd = strxdata
    
    print(strbegin)
    print(strdatalen)
    print(strend)
    print(strxor)
    print(strcmd)

    checklen =int(len(strcmd)/2)
    print(checklen)
    print(strdatalen)
    #check datalength bengin end
    if ((strbegin == '02')&(strend== '03')):
        #get xornum
        datalenH = strdatalen[0]+strdatalen[1]
        datalenL = strdatalen[2]+strdatalen[3]
        datalenH = int(datalenH,16)
        datalenL = int(datalenL,16)
        xornum = int(strbegin,16)
        xornum = xornum ^ datalenH
        xornum = xornum ^ datalenL
        num_datalist = []
        str_datalist = []
        for i in range (checklen)[::1]:
            str_datalist.append(strcmd[i*2:i*2+2])
        print(str_datalist)
        for i in range (checklen):   
            num_datalist.append(int(str_datalist[i],16))
            xornum = xornum ^ num_datalist[i]
        print(num_datalist)
        xornum = hex(xornum)
        xornum = xornum[2:]
        #check xor
        if(strxor[0]=="0"):
            strxor=strxor[1:]
        if(xornum == strxor):
            print(xornum)
            return 1
        else:
            print("55")
            return 0
    else:
        print("56")
        return 0
        #print(xornum)


ser = serial.Serial('/dev/ttyUSB0',9600,timeout = 1.5)

#ms-machineset;cs-cardset,success:0,faile:1
#in timeflag=time1time2times(3byte) time1:buzze time time2:stop time
#timeflag example:050204
def msbuzzer(timeflag):
    if not(isinstance(timeflag,str)):
        timeflag = str(timeflag)
    xdata = "0xC013"+timeflag
    datasend = setdata(xdata)
    datasend = datasend.decode("hex")
    ser.write(datasend)
    datarcv = ser.readline()
    datarcv = binascii.b2a_hex(datarcv)
    print(datarcv)
    print(type(datarcv))
    if(checkdata(datarcv)):
        if(datarcv[9]=="0"):
            return 0
        else:
            return 1
     else:
         return 51

#bpsflag:00:9600 01:19200 02:38400 03:57600  04:115200
def msbp(bpsflag):
    if not(isinstance(bpsflag,str)):
        bpsflag = str(bpsflag)
    xdata = "C01000"+bpsflag
    datasend = setdata(xdata)
    datasend = datasend.decode("hex")
    ser.write(datasend)
    datarcv = ser.readline()
    datarcv = binascii.b2a_hex(datarcv)
    if not(isinstance(datarcv,str)):
        datarcv = str(datarcv)
    if(checkdata(datarcv)):
        if(datarcv[9]=="0"):
            return 0
        else:
            return 1
    else:
        return 51

#modeflag normal mode :00   split mode :01
def msmode(modeflag):
    if not(isinstance(modeflag,str)):
        modeflag = str(modeflag)
    xdata = "0xC01100"+ modeflag
    datasend = setdata(xdata)
    datasend = datasend.decode("hex")
    ser.write(datasend)
    datarcv = ser.readline()
    datarcv = binascii.b2a_hex(datarcv)
    if not(isinstance(datarcv,str)):
        datarcv = str(datarcv)
    if(checkdata(datarcv)):
        if(datarcv[9]=="0"):
            return 0
        else:
            return 1
    else:
        return 51

#return 0:error  number :machine version
def msreadversion():
    xdata = "0xC012"
    datasend = setdata(xdata)
    datasend = datasend.decode("hex")
    ser.write(datasend)
    datarcv = ser.readline()
    datarcv = binascii.b2a_hex(datarcv)
    if not(isinstance(datarcv,str)):
        datarcv = str(datarcv)
    if(checkdata(datarcv)):
        if(datarcv[9]=="0"):
            datarcv = datarcv[10:]
            datarcv = datarcv[:-4]
            return datarcv
        else:
            return 1
    else:
        return 51




#timeflag: 0: close RF other(01-FF)reset time
def msresetRF(timeflag):
    if not(isinstance(timeflag,str)):
        flag = str(timeflag)
    xdata = "0xC015"+timeflag
    datasend = setdata(xdata)
    datasend = datasend.decode("hex")
    ser.write(datasend)
    datarcv = ser.readline()
    datarcv = binascii.b2a_hex(datarcv)
    if not(isinstance(datarcv,str)):
        datarcv = str(datarcv)
    if(checkdata(datarcv)):
        if(datarcv[9]=="0"):
            return 0
        else:
            return 1
    else:
        return 51
#codeflag=mode(1)+ address(1)+code(6)
#mode: 00: A code 04:B code  address 0-15???? 
def msloadm1code(codeflag):
    if not(isinstance(codeflag,str)):
        codeflag = str(codeflag)
    xdata = "0xC016"+codeflag
    datasend = setdata(xdata)
    datasend = datasend.decode("hex")
    ser.write(datasend)
    datarcv = ser.readline()
    datarcv = binascii.b2a_hex(datarcv)
    if not(isinstance(datarcv,str)):
        datarcv = str(datarcv)
    if(checkdata(datarcv)):
        if(datarcv[9]=="0"):
            return 0
        else:
            return 1
    else:
        return 51   

# cs****  return 6:no respond 7:error 

def csstop():
    xdata = "0xC14A"
    datasend = setdata(xdata)
    datasend = datasend.decode("hex")
    ser.write(datasend)
    datarcv = ser.readline()
    datarcv = binascii.b2a_hex(datarcv)
    if not(isinstance(datarcv,str)):
        datarcv = str(datarcv)
    if(checkdata(datarcv)):
        if(datarcv[9]=="0"):
            return 0
        elif(datarcv[9]=="6"):
            return 6
        else:
            return 7
    else:
        return 51


#addressflag=address1(1)+address2(1) data in add1 will cover data in add2
    #exp:0203
def csrecovery(addressflag):
    if not(isinstance(addressflag,str)):
        addressflag = str(addressflag)
    xdata = "0xC149"+addressflag
    datasend = setdata(xdata)
    datasend = datasend.decode("hex")
    ser.write(datasend)
    datarcv = ser.readline()
    datarcv = binascii.b2a_hex(datarcv)
    if not(isinstance(datarcv,str)):
        datarcv = str(datarcv)
    if(checkdata(datarcv)):
        if(datarcv[9]=="0"):
            return 0
        elif(datarcv[9]=="6"):
            return 6
        else:
            return 7
    else:
        return 51

#minusflag=address(1)+data(4)
def csminus(minusflag):
    if not(isinstance(minusflag,str)):
        minusflag = str(minusflag)
    xdata = "0xC148"+minusflag
    datasend = setdata(xdata)
    datasend = datasend.decode("hex")
    ser.write(datasend)
    datarcv = ser.readline()
    datarcv = binascii.b2a_hex(datarcv)
    if not(isinstance(datarcv,str)):
        datarcv = str(datarcv)
    if(checkdata(datarcv)):
        if(datarcv[9]=="0"):
            return 0
        elif(datarcv[9]=="6"):
            return 6
        else:
            return 7
    else:
        return 51


#addflag=address(1)+data(4)
def csadd(addflag):
    if not(isinstance(addflag,str)):
        addflag = str(addflag)
    xdata = "0xC147"+addflag
    datasend = setdata(xdata)
    datasend = datasend.decode("hex")
    ser.write(datasend)
    datarcv = ser.readline()
    datarcv = binascii.b2a_hex(datarcv)
    if not(isinstance(datarcv,str)):
        datarcv = str(datarcv)
    if(checkdata(datarcv)):
        if(datarcv[9]=="0"):
            return 0
        elif(datarcv[9]=="6"):
            return 6
        else:
            return 7
    else:
        return 51

#readflag=address(1)  exp:"01"/"02"....
def csread(readflag):
    if not(isinstance(readflag,str)):
        readflag = str(readflag)
    xdata = "0xC146"+ readflag
    datasend = setdata(xdata)
    datasend = datasend.decode("hex")
    ser.write(datasend)
    datarcv = ser.readline()
    datarcv = binascii.b2a_hex(datarcv)
    if not(isinstance(datarcv,str)):
        datarcv = str(datarcv)
    if(checkdata(datarcv)):
        if(datarcv[9]=="0"):
            datarcv = datarcv[10:]
            datarcv = datarcv[:-4]
            return datarcv
        elif(datarcv[9]=="6"):
            return 6
        else:
            return 7
    else:
        return 51

#initflag=address(1)+data(4)
def csinit(initflag):
    if not(isinstance(initflag,str)):
        initflag = str(initflag)
    xdata = "0xC145"+initflag
    datasend = setdata(xdata)
    datasend = datasend.decode("hex")
    ser.write(datasend)
    datarcv = ser.readline()
    datarcv = binascii.b2a_hex(datarcv)
    if not(isinstance(datarcv,str)):
        datarcv = str(datarcv)
    if(checkdata(datarcv)):
        if(datarcv[9]=="0"):
            return 0
        elif(datarcv[9]=="6"):
            return 6
        else:
            return 7
    else:
        return 51


#writeflag=address(1)+data(16)
def cswriteaddress(writeflag):
    if not(isinstance(writeflag,str)):
        writeflag = str(writeflag)
    xdata = "0xC144"+writeflag
    datasend = setdata(xdata)
    datasend = datasend.decode("hex")
    ser.write(datasend)
    datarcv = ser.readline()
    datarcv = binascii.b2a_hex(datarcv)
    if not(isinstance(datarcv,str)):
        datarcv = str(datarcv)
    if(checkdata(datarcv)):
        if(datarcv[9]=="0"):
            return 0
        elif(datarcv[9]=="6"):
            return 6
        else:
            return 7
    else:
        return 51

#readflag=address(1)
def csreadaddress(readflag):
    if not(isinstance(readflag,str)):
        readflag = str(readflag)
    xdata = "0xC143"+readflag
    datasend = setdata(xdata)
    datasend = datasend.decode("hex")
    ser.write(datasend)
    datarcv = ser.readline()
    datarcv = binascii.b2a_hex(datarcv)
    if not(isinstance(datarcv,str)):
        datarcv = str(datarcv)
    if(checkdata(datarcv)):
        if(datarcv[9]=="0"):
            datarcv = datarcv[10:]
            datarcv = datarcv[:-4]
            return datarcv
        elif(datarcv[9]=="6"):
            return 6
        else:
            return 7
    else:
        return 51



#checkincodeflag=mode(1)+address(1)+code(6)
#mode:00  A code 04 B code
#compare input code with code on card 
def cscheckincode(checkincodeflag):
    if not(isinstance(checkincodeflag,str)):
        checkincodeflag = str(checkincodeflag)
    xdata = "0xC142"+checkincodeflag
    datasend = setdata(xdata)
    datasend = datasend.decode("hex")
    ser.write(datasend)
    datarcv = ser.readline()
    datarcv = binascii.b2a_hex(datarcv)
    if not(isinstance(datarcv,str)):
        datarcv = str(datarcv)
    if(checkdata(datarcv)):
        if(datarcv[9]=="0"):
            return 0
        elif(datarcv[9]=="5"):
            return 5
        elif(datarcv[9]=="6"):
            return 6
        else:
            return 7
    else:
        return 51



#checksetcodeflag=mode(1)+address1(1)+address2(1)
#mode:00:  A code   04: B code
#compare card code with code on system 
def cschecksetcode(checksetcodeflag):
    if not(isinstance(checksetcodeflag,str)):
        checksetcodeflag = str(checksetcodeflag)
    xdata = "0xC141"+checksetcodeflag
    datasend = setdata(xdata)
    datasend = datasend.decode("hex")
    ser.write(datasend)
    datarcv = ser.readline()
    datarcv = binascii.b2a_hex(datarcv)
    if not(isinstance(datarcv,str)):
        datarcv = str(datarcv)
    if(checkdata(datarcv)):
        if(datarcv[9]=="0"):
            return 0
        else:
            return 5
    else:
        return 51




#searchflag=delaytime(2)+mode(1)
#delaytime     exp :123400  (4.66s)
def cssearchm1(searchflag):
    if not(isinstance(searchflag,str)):
        searchflag = str(searchflag)
    xdata = "0xC140"+searchflag
    datasend = setdata(xdata)
    datasend = datasend.decode("hex")
    ser.write(datasend)
    datarcv = ser.read(100)
    datarcv = binascii.b2a_hex(datarcv)
    if not(isinstance(datarcv,str)):
        datarcv = str(datarcv)
    if(checkdata(datarcv)):
        if(datarcv[9]=="0"):
            datarcv = datarcv[10:]
            datarcv = datarcv[:-4]
            return datarcv
        elif(datarcv[9]=="6"):
            return 6
        else:
            return 9
    else:
        return 51



def cscommand(commandflag):
    if not(isinstance(commandflag,str)):
        commandflag = str(commandflag)
    xdata = "0xC126"+commandflag
    datasend = setdata(xdata)
    datasend = datasend.decode("hex")
    ser.write(datasend)
    datarcv = ser.readline()
    datarcv = binascii.b2a_hex(datarcv)
    if not(isinstance(datarcv,str)):
        datarcv = str(datarcv)
    if(checkdata(datarcv)):
        if(datarcv[9]=="0"):
            datarcv = datarcv[10:]
            datarcv = datarcv[:-4]
            return datarcv
        if(datarcv[6]=="2"):
            if(datarcv[9]=="1"):
                return 21
            elif(datarcv[9]=="4"):
                return 24
            elif(datarcv[9]=="6"):
                return 26
            else:
                return 27
        else:
            if(datarcv[9]=="1"):
                return 31
            elif(datarcv[9]=="4"):
                return 34
            elif(datarcv[9]=="6"):
                return 36
            else:
                return 37
    else:
        return 51



#moveflag=delaytime(2)
#delaytime exp :1234  (4.66s)
def csmovecard(moveflag):
    if not(isinstance(moveflag,str)):
        moveflag = str(moveflag)
    xdata = "0xC125"+moveflag
    datasend = setdata(xdata)
    datasend = datasend.decode("hex")
    ser.write(datasend)
    datarcv = ser.readline()
    datarcv = binascii.b2a_hex(datarcv)
    if not(isinstance(datarcv,str)):
        datarcv = str(datarcv)
    if(checkdata(datarcv)):
        if(datarcv[9]=="0"):
            return 0
        elif(datarcv[9]=="1"):
            return 1
        elif(datarcv[9]=="6"):
            return 6
        else:
            return 8
    else:
        return 51



#activeflag=delaytime(2)
#delaytime exp :1234  (4.66s)
def csactivecard(activeflag):
    if not(isinstance(activeflag,str)):
        activeflag = str(activeflag)
    xdata = "0xC124"+activeflag
    datasend = setdata(xdata)
    datasend = datasend.decode("hex")
    ser.write(datasend)
    datarcv = ser.readline()
    datarcv = binascii.b2a_hex(datarcv)
    if not(isinstance(datarcv,str)):
        datarcv = str(datarcv)
    if(checkdata(datarcv)):
        if(datarcv[9]=="0"):
            datarcv = datarcv[10:]
            datarcv = datarcv[:-4]
            return datarcv
        elif(datarcv[9]=="1"):
            return 1
        elif(datarcv[9]=="5"):
            return 5
        elif(datarcv[9]=="6"):
            return 6
        else:
            return 9
    else:
        return 51





def cspowercard():
    xdata = "0xC122000010"
    datasend = setdata(xdata)
    datasend = datasend.decode("hex")
    ser.write(datasend)
    datarcv = ser.readline()
    datarcv = binascii.b2a_hex(datarcv)
    if not(isinstance(datarcv,str)):
        datarcv = str(datarcv)
    if(checkdata(datarcv)):
        if(datarcv[9]=="0"):
            datarcv = datarcv[10:]
            datarcv = datarcv[:-4]
            return datarcv
        elif(datarcv[9]=="1"):
            return 1
        else:
            return 5
    else:
        return 51




