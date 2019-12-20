# -*- coding:utf8 -*-

import requests
import simplejson as json
import time
import re
import logging
import pymysql as mysql
import threading


# ##公共参数###
USERNAME = 'root'
PASSWORD = 'raisecom@2017'
Management_IP = "192.168.205.49"
EMS_DB_USERNAME = "root"
EMS_DB_PASSWORD = "hss"
logging.basicConfig(filename='VpbxEmsConfig.log', level=logging.INFO, datefmt='%m/%d/%Y %I:%M:%S %p'
                    , format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# ##EMS API###
VCODE_API = "http://%s/api/v1/uiframe/icode"
TOKEN_API = "http://%s/api/v1/uiframe/login"
TENANT_API = "http://%s/api/v1/commoncfg/tenancy"
SIPGROUP_API = "http://%s/api/v1/commoncfg/sipGroup"


class VpbxEmsConfig():
    """VPX网管EMS配置的基础类，包含了各业务配置项的配置方法，供自动化配置调用"""

    def __init__(self, Management_IP=Management_IP):
        self.managementIp = Management_IP
        self.userName = USERNAME
        self.vcodeApi = VCODE_API % self.managementIp
        self.tokenApi = TOKEN_API % self.managementIp
        self.tenantApi = TENANT_API % self.managementIp
        self.sipgroup_api = SIPGROUP_API % self.managementIp
        self.vcode = requests.get(url=self.vcodeApi).text
        self.headersTmp = {'Content-Type': 'application/x-www-form-urlencoded'}
        body = {"username":  self.userName, "domains":  [], "tenantId":  "null", "userType":  "1",
             "password":  "RCMfGAQa/XeKc+jCmYQDHg==", "isEncypted":  "true", "vcode":  self.vcode}
        r = requests.post(url=self.tokenApi, headers=self.headersTmp, data=json.dumps(body))
        self.scode = re.findall(r'scode=(.*?);', r.headers['Set-Cookie'])
        self.headers = {'Content-Type': 'application/json', 'Cookie': 'scode= ' + self.scode[0]}

    def my_requests(self, method, api, body):
        """
        自定义封装的requests方法，
        :param method: http请求方法，包括：get、put、post、delete
        :param api: http请求的api地址
        :param body: http请求携带的body体
        :return: http请求的结果，返回值是一个字典，字典包含了http请求的响应码和响应消息，{'status_code': '', 'text': ''}
        """
        header = self.headers
        data = json.dumps(body)
        ret = {'status_code': '', 'text': ''}
        if method == 'get':
            r = requests.get(url=api, headers=header, data=data)
            ret['status_code'] = r.status_code
            ret['text'] = r.text
        elif method == 'post':
            r = requests.post(url=api, headers=header, data=data)
            ret['status_code'] = r.status_code
            ret['text'] = r.text
        elif method == 'put':
            r = requests.put(url=api, headers=header, data=data)
            ret['status_code'] = r.status_code
            ret['text'] = r.text
        elif method == 'delete':
            r = requests.delete(url=api, headers=header, data=data)
            ret['status_code'] = r.status_code
            ret['text'] = r.text
        return ret

    def db_operate(self, table, keys=(), values=(), where=(), method="select", ip=Management_IP, username=EMS_DB_USERNAME
                   , passwd=EMS_DB_PASSWORD, database="cloudasc", port=3306):
        """
            数据库操作：
                通过传入的values、keys、where等参数，完成对Mysql数据库的select、insert、update、delete的操作
            参数：
                    table:参数类型是字符串，要操作的数据库表名
                    keys:参数的类型是元组，元组值个数不限制
                    values:参数的类型是元组，元组值个数不限制，一般作为insert、update插入或者更新的值
                    where:参数的类型是元组，元组的值个数是2个，第一个值作为过滤条件的key，第一个值作为过滤条件的value
                          当前只支持一个过滤条件
                        e.g. select keys[0] from table where where[0]=where[1]
            默认参数：
                    method：要进行数据操作的方法，默认值：select
                    ip：数据库ip地址，默认值：ems的管理地址
                    username：数据库用户名，默认值："root"
                    passwd：数据库密码，默认值："hss"
                    database：数据库名称，默认值："cloudasc"
                    port：数据库端口，默认值：23306
            返回值：select查询操作提供返回值，返回值类型是元组
        """
        db = mysql.connect(ip, username, passwd, "cloudasc", port, charset='utf8')
        cursor = db.cursor()
        ret = []
        if method == "select":
            for i in range(len(keys)):
                sql = "select %s from %s where %s='%s'" % (keys[i], table, where[0], where[1])
                cursor.execute(sql)
                ret.append(cursor.fetchone()[0])
            logging.info("mysql select operate successful, return: %s\n" % ret)
        elif method == "insert":
            for i in range(len(keys)):
                sql = "insert into %s %s values '%s'" % (table, keys[i], values[i])
                cursor.execute(sql)
                db.commit()
            logging.info("mysql insert operate successful\n")
        elif method == "update":
            for i in range(len(keys)):
                sql = "update %s set %s='%s' where %s='%s'" % (table, keys[i], values[i], where[0], where[1])
                cursor.execute(sql)
                db.commit()
            logging.info("mysql update operate successful\n")
        elif method == "delete":
            for i in range(len(keys)):
                sql = "delete from %s where %s='%s'" % (table, where[0], where[1])
                cursor.execute(sql)
                db.commit()
            logging.info("mysql delete operate successful\n")
        cursor.close()
        db.close()
        return tuple(ret)

# ------------------------------------------------ Tenant Method Start ------------------------------------------------#
    
    def add_tenant(self, name, damain, id=0, tenancyid=0, busid=101, aucibcinfo='default', usernum=100, tdrmnum=0, tmcnum=2,
                   pmsinum=2, cgflag=1, homerealm=1):
        """
            新增租户:
            参数：租户名、域名
            默认参数：id=0、tenancyid=0、busid=101、aucibcinfo='default'
                      最大用户数usernum=100、录音通道数量tdrmnum=0、话务台容量tmcnum=2
                      酒管容量pmsinum=2、计费开关cgflag=1（1代表打开、0代表关闭）
                      所属域homerealm=1（1代表系统域）
        """
        logging.info("begin add tenant")
        body = {"id": id, "tenancyId": tenancyid, "tenancyName": name, "bussunitsId": busid, "tenancyDomain": damain,
                "aucSbcInfo": aucibcinfo, "userMaxNum": usernum, "tdrmMaxNum": tdrmnum, "tmcMaxNum": tmcnum,
                "pmsiMaxNum": pmsinum, "cgFlag": cgflag, "homeRealm": homerealm}
        r = requests.put(url=self.tenantApi, headers=self.headers, data=json.dumps(body))
        logging.info("tenant info: %s" % str(body))
        if r.status_code == 200:
            logging.info("add tenant successful\n")
            return 1
        else:
            logging.error("add tenant failed, response code = %d, error: %s\n" % (r.status_code, r.text))
            return 0

    def del_tenant(self, name, damain, busid=101, aucibcinfo='default', usernum=100, tdrmnum=0, tmcnum=2,
                   pmsinum=2, cgflag=1, homerealm=1):
        """
            删除租户:
            参数：租户名、域名
            默认参数： id=查询值、tenancyid=查询值、busid=101、aucibcinfo='default'
                      最大用户数usernum=100、录音通道数量tdrmnum=0、话务台容量tmcnum=2
                      酒管容量pmsinum=2、计费开关cgflag=1（1代表打开、0代表关闭）
                      所属域homerealm=1（1代表系统域）
        """
        logging.info("begin delete tenant")
        db_response = self.db_operate('tenant', keys=('id', 'tenancy_id'), where=('tenancy_domain', damain))
        body = {"id": db_response[0], "tenancyId": db_response[1], "tenancyName": name, "bussunitsId": busid, "tenancyDomain": damain,
                "aucSbcInfo": aucibcinfo, "userMaxNum": usernum, "tdrmMaxNum": tdrmnum, "tmcMaxNum": tmcnum,
                "pmsiMaxNum": pmsinum, "cgFlag": cgflag, "homeRealm": homerealm}
        r = requests.delete(url=self.tenantApi, headers=self.headers, data=json.dumps(body))
        logging.info("tenant info: %s" % str(body))
        if r.status_code == 200:
            logging.info("delete tenant successful\n")
            return 1
        else:
            logging.error("delete tenant failed, response code = %d, error: %s\n" % (r.status_code, r.text))
            return 0

    def modify_tenant(self, name, damain, busid=101, aucibcinfo='default', usernum=10, tdrmnum=0, tmcnum=2,
                   pmsinum=2, cgflag=1, homerealm=1):
        """
            修改租户:
            参数：租户名、域名
            默认参数：id=查询值、tenancyid=查询值、busid=101、aucibcinfo='default'
                      最大用户数usernum=100、录音通道数量tdrmnum=0、话务台容量tmcnum=2
                      酒管容量pmsinum=2、计费开关cgflag=1（1代表打开、0代表关闭）
                      所属域homerealm=1（1代表系统域）
        """
        logging.info("begin modify tenant")
        db_response = self.db_operate('tenant', keys=('id', 'tenancy_id'), where=('tenancy_domain', damain))
        body = {"id": db_response[0], "tenancyId": db_response[1], "tenancyName": name, "bussunitsId": busid, "tenancyDomain": damain,
                "aucSbcInfo": aucibcinfo, "userMaxNum": usernum, "tdrmMaxNum": tdrmnum, "tmcMaxNum": tmcnum,
                "pmsiMaxNum": pmsinum, "cgFlag": cgflag, "homeRealm": homerealm}
        r = requests.post(url=self.tenantApi, headers=self.headers, data=json.dumps(body))
        logging.info("tenant info: %s" % str(body))
        if r.status_code == 200:
            logging.info("modify tenant successful\n")
            return 1
        else:
            logging.error("modify tenant failed, response code = %d, error: %s\n" % (r.status_code, r.text))
            return 0

# ------------------------------------------------- Tenant Method End -------------------------------------------------#

# ------------------------------------------ Reg_Public_Number Method Start -------------------------------------------#

    def add_reg_public_number(self, pui, pvi, pwd, numinterval=1, totalnum=1):
        """
            新增注册公网号码:
            参数：公网号码、认证名、认证密码
            默认参数：号码步长和号码总数的默认值：1
        """
        logging.info("begin add public number")
        self.sipgroup_api = "http://%s/api/v1/commoncfg/sipGroup" % self.managementIp
        body = {"aucPui":  pui, "aucPvi":  pvi, "ulNumInterval":  numinterval, "ulTotalNum":  totalnum,
             "aucPwd":  pwd}
        r = requests.put(url=self.sipgroup_api, headers=self.headers, data=json.dumps(body))
        logging.info("public number info: %s" % str(body))
        if r.status_code == 200:
            logging.info("add public number successful\n")
            return 1
        else:
            logging.error("add public number failed, response code = %d, error: %s\n" % (r.status_code, r.text))
            return 0

    def del_reg_public_number(self, pui, pvi=None, pwd=None, numinterval=1, totalnum=1):
        """
            删除注册公网号码:
            参数：公网号码,认证名和认证密码可以携带
            默认参数：号码步长和号码总数的默认值：1
        """
        logging.info("begin delete public number")
        body = {"aucPui":  pui, "aucPvi":  pvi, "aucPwd":  pwd, "aucTenantInfo":  "", "operation":  "",
             "ucState":  "0", "ulNumInterval":  numinterval, "ulTotalNum":  totalnum}
        r = requests.delete(url=self.sipgroup_api, headers=self.headers, data=json.dumps(body))
        logging.info("public number info: %s" % str(body))
        if r.status_code == 200:
            logging.info("delete public number successful\n")
            return 1
        else:
            logging.error("delete public number failed, response code = %d, error: %s\n" % (r.status_code, r.text))
            return 0

    def modify_reg_public_number(self, pui, pvi, pwd):
        """
            修改注册公网号码:
            参数：认证名、认证密码
            默认参数：号码步长和号码总数的默认值：1，公网号码不可修改
        """
        logging.info("begin modify public number")
        body = {"aucPui":  pui, "aucPvi":  pvi, "ulNumInterval":  "1", "ulTotalNum":  "1", "aucPwd":  pwd}
        r = requests.post(url=self.sipgroup_api, headers=self.headers, data=json.dumps(body))
        logging.info("public number info: %s" % str(body))
        print(r.status_code, r.text)
        if r.status_code == 200:
            logging.info("modify public number successful")
            return 1
        else:
            logging.error("modify public number failed, response code = %d, error: %s\n" % (r.status_code, r.text))
            return 0

# ------------------------------------------- Reg_Public_Number Method End --------------------------------------------#

    def qu(self):
        api1 = 'http://192.168.205.49/api/v1/commoncfg/shell/set'
        body = {"unitID":"101","aucShCmd":"imp_spms_uac_show"}
        r = requests.post(url=api1, headers=self.headers, data=json.dumps(body))
        print(r.status_code)
        print(r.text)

        api2 = 'http://192.168.205.49/api/v1/commoncfg/shell/getResult?unitID=101'
        while True:
            r = requests.get(url=api2, headers=self.headers)
            print(r.json()['rows'][0]['isEnd'])
            print(r.json()['rows'][0]['aucShCmdRsp'])
            if r.json()['rows'][0]['isEnd'] == 1:
                break


def my_thread(method, args):
    threads = []
    for x in range(len(args)):
        t = threading.Thread(target=method, args=args[x])
        threads.append(t)
    for y in threads:
        y.setDaemon(True)
        y.start()
    for y in threads:
        y.join()

if __name__ == '__main__':
    aa = VpbxEmsConfig()
    # aa.add_reg_public_number('22222', '7555', '555')
#     time.sleep(2)
#     aa.modify_reg_public_number('22222', '22222222', '551')
#     time.sleep(2)
#     aa.del_reg_public_number('22222')
#     aa.add_tenant("wxl1", "auto1.com", usernum=200)
#     time.sleep(2)
#     aa.modify_tenant("wxl1", "auto1.com", usernum=10)
#     time.sleep(2)
#     aa.del_tenant("wxl1", "auto1.com")

    aa.qu()



