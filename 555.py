# -*- coding:utf8 -*-
__author__ = 'lei'

import requests
import base64
import simplejson as json
import time
import pymysql as MySQLdb
import re
import paramiko
import telnetlib
from prettytable import PrettyTable

SO_USERNAME = 'administrator'
SO_PASSWORD = 'raisecom'
SO_IP = "192.168.193.253"
CPE_USERNAME = 'telecomadmin'
CPE_PASSWORD = b'nE7jA%5m'
CPE_PORT = 23
# ##SO API###
SO_TOKEN_API = "http://%s:3000/api/v1/tokens"
SO_ACCELERATE_API = "http://%s:3000/api/service/accelerate/"

firstcpe = 13
endcpe = 54

cpes = list(range(1000000 + firstcpe, endcpe + 1000001))
cpes.remove(1000014)

transactionId = {}

class Cloud:
    # 云业务配置的增删改查

    def __init__(self, SO_IP=SO_IP, SO_USERNAME=SO_USERNAME, SO_PASSWORD=SO_PASSWORD, SO_TOKEN_API=SO_TOKEN_API,
                 SO_ACCELERATE_API=SO_ACCELERATE_API):
        self.soIp = SO_IP
        self.soUserName = SO_USERNAME
        self.soPassword = SO_PASSWORD
        self.soTokenApi = SO_TOKEN_API % self.soIp
        self.soAccelerateApi = SO_ACCELERATE_API % self.soIp
        self.base64string = base64.b64encode((self.soUserName + ':' + self.soPassword).encode())
        self.headersTmp = {'Content-Type': 'application/json', 'Authorization': 'Basic ' + self.base64string.decode()}
        # self.soToken = requests.get(url=self.soTokenApi, headers=self.headersTmp).json()["scode"]
        # self.headers = {'Content-Type': 'application/json', 'Authorization': 'Basic ' + self.base64string,'Cookie': "scode = "+self.soToken}

    @staticmethod
    def seqnumber():
        t = time.strftime("%y%m%d%H%M%S", time.localtime())
        seqnumber = '525' + t
        return seqnumber

    def transactionid(self):
        t = time.strftime("%y%m%d%H%M%S", time.localtime())
        transactid = '526' + t
        return transactid

    def sum(self, title, datas):
        self.tb = PrettyTable(title)
        self.tb.add_row(datas)
        print('')
        print('')
        print("执行结果统计：")
        print(self.tb)
        print('')

    def add_acc_business(self, firstcpe, endcpe):
        self.firstcpe = firstcpe
        self.endcpe = endcpe
        self.logicid = 1000000
        self.userId = "wxl0000"
        self.ad = 5270000
        s_sum = 0
        f_sum = 0
        f_list = ''
        area = ['高新', '曲江', '雁塔', '长安']
        self.acccreaturl = self.soAccelerateApi + 'creation'
        for k in range(firstcpe, endcpe + 1):
            body = {"serviceType": 2, "bandWidth": 5, "ipList": ["45.76.231.7"], "duration": 12}
            body["sequenceNo"] = self.seqnumber()
            body["transactionId"] = self.transactionid()
            body["logicId"] = str(self.logicid + k)
            body["userId"] = 'wxl0000' + str(k)
            body["ad"] = str(self.ad + k)
            response = requests.post(url=self.acccreaturl, headers=self.headersTmp, data=json.dumps(body))
            time.sleep(3)
            #print(response.status_code, response.text)
            if response.status_code == 200:
                s_sum += 1
                print("###### %s's accelerate business request SUCCESS ######" % body["userId"])
            else:
                f_sum += 1
                f_list = f_list + str(k) + ' '
                print("###### %s's accelerate business request FAILED ######" % body["userId"])
        if f_sum:
            title = ["CPE总数", "成功个数", "失败个数", "失败详情"]
            datas = [self.endcpe + 1 - self.firstcpe, s_sum, f_sum, f_list]
            self.sum(title, datas)
        else:
            title = ["CPE总数", "成功个数", "失败个数"]
            datas = [self.endcpe+1-self.firstcpe, s_sum, f_sum]
            self.sum(title, datas)

    def del_acc_business(self, firstcpe, endcpe):
        self.firstcpe = firstcpe
        self.endcpe = endcpe
        s_sum = 0
        f_sum = 0
        f_list = ''
        self.accdeleteurl = self.soAccelerateApi + 'deletion'
        for k in range(firstcpe, endcpe + 1):
            logicid = str(1000000 + k)
            # 打开数据库连接
            db = MySQLdb.connect(self.soIp, "root", "raisecom@123", "so_order", 23306, charset='utf8')
            # 使用cursor()方法获取操作游标
            cursor = db.cursor()
            mysql = "select transactionId from %s where logicId=%s" % ('worker_order_business', logicid)
            cursor.execute(mysql)
            transactionId = cursor.fetchone()
            db.close()
            seqnumber = self.seqnumber()
            body = {"sequenceNo": seqnumber, "transactionId": transactionId[0], "logicId": logicid}
            response = requests.post(url=self.accdeleteurl, headers=self.headersTmp, data=json.dumps(body))
            print(response.status_code, response.text)
            time.sleep(2)
            if response.status_code == 200:
                s_sum += 1
                print("###### LogicId %s's acc business delete SUCCESS ######" % logicid)
            else:
                f_sum += 1
                f_list = f_list + str(k) + ' '
                print("###### LogicId %s's acc business delete FAILED ######" % logicid)
        if f_sum:
            title = ["CPE总数", "成功个数", "失败个数", "失败详情"]
            datas = [self.endcpe + 1 - self.firstcpe, s_sum, f_sum, f_list]
            self.sum(title, datas)
        else:
            title = ["CPE总数", "成功个数", "失败个数"]
            datas = [self.endcpe+1-self.firstcpe, s_sum, f_sum]
            self.sum(title, datas)
