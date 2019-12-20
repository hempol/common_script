# -*- coding:utf8 -*-
__author__ = 'lei'

import requests
import base64
import simplejson as json
import time

BSS_USERNAME = 'admin'
BSS_PASSWORD = 'raisecom'
BSS_IP = "192.168.193.108"

###BSS API###
BSS_TOKEN_API = "http://%s:9001/api/v1/smb/safe/token"
BSS_ACCELERATE_API = "http://%s:9001/api/service/accelerate"
BSS_ACCELERATE_DEL_API = "http://%s:9001/api/service/accelerate/%s"


class Cloud:
    '''云业务配置的增删改查'''

    def __init__(self, BSS_IP=BSS_IP, BSS_USERNAME=BSS_USERNAME,BSS_PASSWORD=BSS_PASSWORD,BSS_TOKEN_API=BSS_TOKEN_API,
                 BSS_ACCELERATE_API=BSS_ACCELERATE_API,BSS_ACCELERATE_DEL_API=BSS_ACCELERATE_DEL_API):
        self.bssIp = BSS_IP
        self.bssUserName = BSS_USERNAME
        self.bssPassword = BSS_PASSWORD
        self.bssTokenApi = BSS_TOKEN_API % self.bssIp
        self.bssAccelerateApi = BSS_ACCELERATE_API % self.bssIp
        self.bssAccelerateDelApi = BSS_ACCELERATE_DEL_API
        self.base64string = base64.b64encode(self.bssUserName + ':' + self.bssPassword)
        self.headersTmp = {'Content-Type':'application/json','Authorization':'Basic '+ self.base64string}
        self.bssToken = requests.get(url=self.bssTokenApi, headers=self.headersTmp).json()["scode"]
        self.headers = {'Content-Type':'application/json','Authorization':'Basic '+ self.base64string,
                        'Cookie':"scode = "+self.bssToken}
    def add_accelerate_business(self,body):
        self.body = body
        self.userId = self.body["userId"]
        response = requests.post(url=self.bssAccelerateApi, headers=self.headers, data=json.dumps(self.body))
        #print response.json()
        if response.status_code == 200:
            print ("###### %s's accelerate business request SUCCESS ######") %self.userId

        else:
            print ("###### %s's accelerate business request FAILED ######") %self.userId
            #raise Exception("###### %s's accelerate business request FAILED ######") %self.userId
    def query_tenant_service_id(self,logicId):
        self.logicid = logicId
        response = requests.get(url=self.bssAccelerateApi, headers=self.headers).json()
        if len(response) == 0:
            print("###### Bss not exist tenant service! ######") %self.logicid
            return
        else:
            for i in range(0,len(response)):
                if int(response[i]["logicId"]) == int(self.logicid):
                    print("###### Tenant service id query SUCCESS ######")
                    print(response[i]["uuid"])
                    return response[i]["uuid"]
    def del_accelerate_business(self,logicId):
        self.logicid = logicId
        tenant_service_id = self.query_tenant_service_id(self.logicid)
        bssAccelerateDelApi = self.bssAccelerateDelApi % (self.bssIp,tenant_service_id)
        response = requests.delete(url=bssAccelerateDelApi, headers=self.headers)
        if response.status_code == 200:
            print ("###### LogicId %s's service delete SUCCESS ######")%self.logicid
        else:
            print ("###### LogicId %s's service delete FAILED ######")%self.logicid

if __name__ == "__main__":
    dz = Cloud()
    first = 14
    end = 14
    body = {"uuid": "string", "clsnId": "SDNC", "serviceType": 1, "ipNumber": 1, "ipList": ["45.76.231.7"],
            "duration": 12, "serviceStatus": 0}
    for i in range(first, end+1):
        body["logicId"] = '10000' + str(i)
        body["userId"] = 'wxl0000' + str(i)
        dz.add_accelerate_business(body)
        time.sleep(15)
        #dz.del_accelerate_business(body["logicId"])







