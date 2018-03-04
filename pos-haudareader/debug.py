#!/usr/bin/python
# -*- coding: utf-8 -*-
#filename:debug.py
import logging
logging.basicConfig(level   = logging.DEBUG,
	                format  ='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
	                datefmt ='%Y %b %d %H:%M:%S',
	                filename='pos.log',
	                filemode='w')
 