call wiringPiSetup(); first


call Bh1750ValueGet() 
return LightValue(int);


Temperature(int)
Humidity(int)
call AM2302ValueGet();>> returnTemperature();>>returnHumidity(); 
return the last test value(not the value of now),
suggest call AM2302ValueGet() twice if sensor has rest for a long time,for exp:
call AM2302ValueGet();>> AM2302ValueGet();>> returnTemperature();>> returnHumidity(); 




call  Dsm501ValueGet()
return DustConcentration1(int) 


