编译.c 生成动态库
gcc -shared -fPIC -I/usr/local/include -L/usr/local/lib -lwiringPi recheck.c -o librecheck.so

使用msprintdriver.py前需要安装wiringpi

