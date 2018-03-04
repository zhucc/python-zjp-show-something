snesor:sensor.o   	
	gcc -o sensor sensor.o -lwiringPi
sensor.o:sensor.c /home/pi/wiringPi/wiringPi/wiringPi.h 
	gcc -c sensor.c 
.PHONY:clean
clean:
	-rm -f *.o
	
