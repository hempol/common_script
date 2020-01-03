# -*- coding:utf8 -*-

import requests
import simplejson as json
import re
import logging
import pymysql as mysql
import time


# ##公共参数###
USERNAME = 'root'
PASSWORD = 'raisecom@2017'
Management_IP = "172.102.201.17"
EMS_DB_USERNAME = "root"
EMS_DB_PASSWORD = "hss"
logging.basicConfig(filename='VpbxEmsConfig.log', level=logging.INFO, datefmt='%m/%d/%Y %I:%M:%S %p'
                    , format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
consoleLog = logging.StreamHandler()
consoleLog.setLevel(logging.DEBUG)
consoleLog.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', '%m/%d/%Y %I:%M:%S %p'))
logging.getLogger('').addHandler(consoleLog)

