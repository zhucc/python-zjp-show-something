#include"wiringPi.h"
#include"stdio.h"

#define TRIG 25
#define ECHO 28

int check()
    {
    int start = 0;
    int end = 0;
    int stime;
    //发送一个10us以上的高电平
    digitalWrite(TRIG,1);
    delayMicroseconds(10);
    digitalWrite(TRIG,0);
    int i,j = 0;
    for(i=0;i<8000;i++)
    {
        if (digitalRead(ECHO) == 1)
        {
    	    start = micros();
	    for(j=0;j<8000;j++)
            {
                if(digitalRead(ECHO) == 0)
                {
	        end = micros();
                break;
	        }
	    }
        break;
        }
    }
    stime = end - start;
    delay(100);  //检测周期至少65ms
    return stime;
}
void init()
{
    wiringPiSetup();
    pinMode(TRIG,OUTPUT);
    pinMode(ECHO,INPUT);
    digitalWrite(TRIG,0);
}

void main()
{
    int arr;
    init();
    int i = 0;
    for(i = 0; i <2; i++)
    {
       arr = check();
    }
}
