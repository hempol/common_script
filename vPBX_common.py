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

# ##EMS API###
VCODE_API = "http://%s/api/v1/uiframe/icode"
TOKEN_API = "http://%s/api/v1/uiframe/login"
TENANT_API = "http://%s/api/v1/commoncfg/tenancy"
SIPGROUP_API = "http://%s/api/v1/commoncfg/sipGroup"
USER_GROUP_API = "http://%s/api/v1/commoncfg/userGroup"
USER_GROUP_PRE_NUM_API = "http://%s/api/v1/commoncfg/userGroupCnacld"           # 用户组字冠
USER_GROUP_PRE_CODE_API = "http://%s/api/v1/commoncfg/userGroupDialPrecode"    # 用户组加拨前缀
SIP_TRUNK = "http://%s/api/v1/commoncfg/sipTrunk"                                # sip中继
SIP_OFFICE = "http://%s/api/v1/commoncfg/officeCfg"                              # sip局向
OUT_BLACK = "http://%s/api/v1/commoncfg/hpui/outBlack"                          # 呼出黑名单
OUT_WHITE = "http://%s/api/v1/commoncfg/hpui/outWhite"                          # 呼出白名单
IN_BLACK = "http://%s/api/v1/commoncfg/hpui/inBlack"                            # 呼入黑名单
IN_WHITE = "http://%s/api/v1/commoncfg/hpui/inWhite"                            # 呼入白名单


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
        body = {"username":   self.userName, "domains":   [], "tenantId":   "null", "userType":   "1",
             "password":   "RCMfGAQa/XeKc+jCmYQDHg==", "isEncypted":   "true", "vcode":   self.vcode}
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
    
    def add_tenant(self, name, damain, id=0, tenancyid=0, busid=101, aucibcinfo='default', usernum=100, tdrmnum=0, tmcnum=0,
                   pmsinum=0, cgflag=0, homerealm=1):
        """
            新增租户:
            参数：租户名、域名
            默认参数：id=0、tenancyid=0、busid=101、aucibcinfo='default'
                      最大用户数usernum=100、录音通道数量tdrmnum=0、话务台容量tmcnum=0
                      酒管容量pmsinum=0、计费开关cgflag=0（1代表打开、0代表关闭）
                      所属域homerealm=1（1代表系统域）
        """
        logging.info("begin add tenant")
        body = {"id":  id, "tenancyId":  tenancyid, "tenancyName":  name, "bussunitsId":  busid, "tenancyDomain":  damain,
                "aucSbcInfo":  aucibcinfo, "userMaxNum":  usernum, "tdrmMaxNum":  tdrmnum, "tmcMaxNum":  tmcnum,
                "pmsiMaxNum":  pmsinum, "cgFlag":  cgflag, "homeRealm":  homerealm}
        r = requests.put(url=self.tenantApi, headers=self.headers, data=json.dumps(body))
        logging.info("tenant info: %s" % str(body))
        if r.status_code == 200:
            logging.info("add tenant successful\n")
            return 1
        else:
            logging.error("add tenant failed, response code = %d, error: %s\n" % (r.status_code, r.text))
            return 0

    def del_tenant(self, name, damain, busid=101, aucibcinfo='default', usernum=100, tdrmnum=0, tmcnum=0,
                   pmsinum=0, cgflag=0, homerealm=1):
        """
            删除租户:
            参数：租户名、域名
            默认参数： id=查询值、tenancyid=查询值、busid=101、aucibcinfo='default'
                      最大用户数usernum=100、录音通道数量tdrmnum=0、话务台容量tmcnum=0
                      酒管容量pmsinum=0、计费开关cgflag=0（1代表打开、0代表关闭）
                      所属域homerealm=1（1代表系统域）
        """
        logging.info("begin delete tenant")
        db_response = self.db_operate('tenant', keys=('id', 'tenancy_id'), where=('tenancy_domain', damain))
        body = {"id":  db_response[0], "tenancyId":  db_response[1], "tenancyName":  name, "bussunitsId":  busid, "tenancyDomain":  damain,
                "aucSbcInfo":  aucibcinfo, "userMaxNum":  usernum, "tdrmMaxNum":  tdrmnum, "tmcMaxNum":  tmcnum,
                "pmsiMaxNum":  pmsinum, "cgFlag":  cgflag, "homeRealm":  homerealm}
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
        body = {"id":  db_response[0], "tenancyId":  db_response[1], "tenancyName":  name, "bussunitsId":  busid, "tenancyDomain":  damain,
                "aucSbcInfo":  aucibcinfo, "userMaxNum":  usernum, "tdrmMaxNum":  tdrmnum, "tmcMaxNum":  tmcnum,
                "pmsiMaxNum":  pmsinum, "cgFlag":  cgflag, "homeRealm":  homerealm}
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
        body = {"aucPui":   pui, "aucPvi":   pvi, "ulNumInterval":   numinterval, "ulTotalNum":   totalnum,
             "aucPwd":   pwd}
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
        body = {"aucPui":   pui, "aucPvi":   pvi, "aucPwd":   pwd, "aucTenantInfo":   "", "operation":   "",
             "ucState":   "0", "ulNumInterval":   numinterval, "ulTotalNum":   totalnum}
        r = requests.delete(url=self.sipgroup_api, headers=self.headers, data=json.dumps(body))
        # logging.info("public number info: %s" % str(body))
        # if r.status_code == 200:
        #     logging.info("delete public number successful\n")
        #     return 1
        # else:
        #     logging.error("delete public number failed, response code = %d, error: %s\n" % (r.status_code, r.text))
        #     return 0

    def modify_reg_public_number(self, pui, pvi, pwd):
        """
            修改注册公网号码:
            参数：认证名、认证密码
            默认参数：号码步长和号码总数的默认值：1，公网号码不可修改
        """
        logging.info("begin modify public number")
        body = {"aucPui":   pui, "aucPvi":   pvi, "ulNumInterval":   "1", "ulTotalNum":   "1", "aucPwd":   pwd}
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
# --------------------------------------------- User_Group Method Start------------------------------------------------#
    def add_user_group(self, tenant, name):
        """
            新增用户组:
            参数：
                tenant：租户名
                name：用户组名
            默认参数：-
            auther:wxl
            date:2019-12-27
        """
        logging.info("begin add user group")
        body = {"aucTenantInfo":  tenant, "aucGroupName":  name, "ulUserGroupId": 0}
        r = requests.put(url=USER_GROUP_API % Management_IP, headers=self.headers, data=json.dumps(body))
        logging.info("user group info: %s" % str(body))
        if r.status_code == 200:
            logging.info("add user group successful\n")
            return 1
        else:
            logging.error("add user group failed, response code = %d, error: %s\n" % (r.status_code, r.text))
            return 0

    def add_user_group_pre_num(self, tenant, name, prenum, officeid=1, minength=5, maxlength=32, calltype=4):
        """
            用户组新增字冠:
            参数：
                tenant：租户名
                name：用户组名
                prenum:字冠
            默认参数：
                officeid:局向号，默认值1
                minength:最小号长，默认值5
                maxlength:最大号长，默认值32
                calltype:业务类型，默认值4，代表出局国际
            auther:wxl
            date:2019-12-27
        """
        logging.info("begin add user group aucPreNum")
        body = {"tenant":  tenant, "ucGroupName":  name, "start": 0, "limit": 0}
        usergroupid_api = "http://%s/api/v1/commoncfg/userGroup?tenant=%s&ucGroupName=%s&start=0&limit=10" % (Management_IP, tenant, name)
        r = requests.get(url=usergroupid_api, headers=self.headers, data=json.dumps(body))
        usergroupid = ''
        if r.status_code == 200:
            if r.json()["total"] == 1:
                if r.json()["rows"]:
                    usergroupid = r.json()["rows"][0]["ulUserGroupId"]
                else:
                    logging.error("query user group aucPreNum id failed，rows为空")
                    return 0
            else:
                logging.error("query user group aucPreNum id failed，total=0")
                return 0
        body= {"aucPreNum":  prenum, "ulUserGroupId":  usergroupid, "aucTenantInfo":  tenant, "usOfficeID":  officeid,
               "ucMinLength":  minength, "ucMaxLength":  maxlength, "ucCallerNumTransTag":  "0", "ucCallerNumMapTag":  "1",
               "ucCallerDIDNumTag":  "1", "ucCalledNumTransTag":  "0", "ucCalledNumMapTag":  "0", "ucCallType":  calltype}
        r = requests.put(url=USER_GROUP_PRE_NUM_API % Management_IP, headers=self.headers, data=json.dumps(body))
        logging.info("user group aucPreNum info: %s" % str(body))
        if r.status_code == 200:
            logging.info("add user group aucPreNum successful\n")
            return 1
        else:
            logging.error("add user group aucPreNum failed, response code = %d, error: %s\n" % (r.status_code, r.text))
            return 0

    def add_user_group_pre_code(self, tenant, name, precode, minength=5, maxlength=32):
        """
            用户组新增加拨前缀:
            参数：
                tenant：租户名
                name：用户组名
                precode:加拨前缀号码
            默认参数：
                minength:最小号长，默认值5
                maxlength:最大号长，默认值32
            auther:wxl
            date:2019-12-27
        """
        logging.info("begin add user group aucPreCode")
        body = {"tenant":  tenant, "ucGroupName":  name, "start": 0, "limit": 0}
        usergroupid_api = "http://%s/api/v1/commoncfg/userGroup?tenant=%s&ucGroupName=%s&start=0&limit=10" % (Management_IP, tenant, name)
        r = requests.get(url=usergroupid_api, headers=self.headers, data=json.dumps(body))
        usergroupid = ''
        if r.status_code == 200:
            if r.json()["total"] == 1:
                if r.json()["rows"]:
                    usergroupid = r.json()["rows"][0]["ulUserGroupId"]
                else:
                    logging.error("query user group aucPreCode id failed，rows为空")
                    return 0
            else:
                logging.error("query user group aucPreCode id failed，total=0")
                return 0
        body= {"aucPreNum": precode, "ulUserGroupId": usergroupid, "aucTenantInfo": tenant, "ucMinLength": minength, "ucMaxLength": maxlength}
        r = requests.put(url=USER_GROUP_PRE_CODE_API % Management_IP, headers=self.headers, data=json.dumps(body))
        logging.info("user group aucPreNum info: %s" % str(body))
        if r.status_code == 200:
            logging.info("add user group aucPreCode successful\n")
            return 1
        else:
            logging.error("add user group aucPreCode failed, response code = %d, error: %s\n" % (r.status_code, r.text))
            return 0

# ----------------------------------------------- User_Group Method End -----------------------------------------------#
# ----------------------------------------------- Sip_Trunk Method Start ----------------------------------------------#
    def add_sip_trunk(self, trunkid, trunkname, ofiiceurl, remoteip=None, remotetype=1):
        """
            新增sip中继:
            参数：
                trunkid：中继号，范围201-400
                trunkname：中继名
                ofiiceurl：对端局域名
            默认参数：
                remoteip：对端IP，默认值None
                remotetype：对端局类型，默认值1； 0代表注册中继，1代表对等中继
            auther:wxl
            date:2019-12-27
        """
        logging.info("begin add sip trunk")
        if remotetype == 1:
            body = {"unitID": "101", "usTrunkID": trunkid, "aucTrunkName": trunkname, "aucSbcInfo": "default",
                    "aucOfiiceUrl": ofiiceurl, "ucRemoteType": remotetype, "aucRemoteIp": remoteip, "usRemotePort": "5060"
                , "ucProtocolType": "0", "ucHeartBeatEnable": "0", "ucHeartBeatPeriod": "", "ucMaxChannel": ""}
            r = requests.put(url=SIP_TRUNK % Management_IP, headers=self.headers, data=json.dumps(body))
            logging.info("user group info: %s" % str(body))
            if r.status_code == 200:
                logging.info("add sip trunk successful\n")
                return 1
            else:
                logging.error("add sip trunk failed0, response code = %d, error: %s\n" % (r.status_code, r.text))
                return 0
        else:
            body = {"unitID": "101", "usTrunkID": trunkid, "aucTrunkName": trunkname, "aucSbcInfo": "default",
                    "aucOfiiceUrl": ofiiceurl, "ucRemoteType": remotetype, "aucRemoteIp": "", "usRemotePort": "",
                    "ucProtocolType": "0", "ucHeartBeatEnable": "0", "ucHeartBeatPeriod": "", "ucMaxChannel": ""}
            r = requests.put(url=SIP_TRUNK % Management_IP, headers=self.headers, data=json.dumps(body))
            logging.info("sip trunk info: %s" % str(body))
            if r.status_code == 200:
                logging.info("add sip trunk successful\n")
                return 1
            else:
                logging.error("add sip trunk failed1, response code = %d, error: %s\n" % (r.status_code, r.text))
                return 0
# ------------------------------------------------ Sip_Trunk Method End -----------------------------------------------#
# ----------------------------------------------- Sip_Office Method Start ---------------------------------------------#

    def add_sip_office(self, officeid, officename):
        """
            新增局向:
            参数：
                officeid：局向号，范围1-1000
                officename：局向名
            默认参数：-
            auther:wxl
            date:2019-12-27
        """
        logging.info("begin add sip office")
        body = {"unitID": "101", "usOfficeID": officeid, "aucOfficeName": officename, "ucTacticsType":"0"}
        r = requests.put(url=SIP_OFFICE % Management_IP, headers=self.headers, data=json.dumps(body))
        logging.info("sip office info: %s" % str(body))
        if r.status_code == 200:
            logging.info("add sip office successful\n")
            return 1
        else:
            logging.error("add sip office failed, response code = %d, error: %s\n" % (r.status_code, r.text))
            return 0
# ------------------------------------------------ Sip_Office Method End ----------------------------------------------#
# ------------------------------------------- Black_White_Number Method Start -----------------------------------------#

    def add_out_black(self, tenant, pui, number):
        """
            新增分机呼出黑名单:
            参数：
                tenant：租户名
                pui：分机号码
                number：呼出黑名单号码
            默认参数：-
            auther:wxl
            date:2019-12-27
        """
        logging.info("begin add out black number")
        body = {"tenant": tenant, "auctenatMum": pui, "start": 0, "limit": 0}
        out_black_number_api = "http://%s/api/v1/commoncfg/hpui/outBlack?tenant=%s&auctenatMum=%s&start=0&limit=10" % (
        Management_IP, tenant, pui)
        r = requests.get(url=out_black_number_api, headers=self.headers, data=json.dumps(body))
        outblacknum = ""
        if r.status_code == 200:
            if r.json()["total"] >= 1:
                if r.json()["rows"]:
                    for i in range(r.json()["total"]):
                        outblacknum += r.json()["rows"][i]["aucAllAddrNum"]
                        outblacknum += ','
                else:
                    logging.error("query out black number failed，rows为空")
                    return 0
        outblacknum += str(number)
        body = {"aucTenantInfo": tenant, "aucPui": pui, "aucAllAddrNum": outblacknum}
        if r.json()["total"] == 0:
            res = requests.put(url=OUT_BLACK % Management_IP, headers=self.headers, data=json.dumps(body))
            logging.info("out black number info: %s" % str(body))
            if res.status_code == 200:
                logging.info("add out black number successful\n")
                return 1
            else:
                logging.error("add out black number failed, response code = %d, error: %s\n" % (r.status_code, r.text))
                return 0
        else:
            res = requests.post(url=OUT_BLACK % Management_IP, headers=self.headers, data=json.dumps(body))
            logging.info("out black number info: %s" % str(body))
            if res.status_code == 200:
                logging.info("add out black number successful\n")
                return 1
            else:
                logging.error("add out black number failed, response code = %d, error: %s\n" % (r.status_code, r.text))
                return 0

    def add_out_white(self, tenant, pui, number):
        """
            新增分机呼出白名单:
            参数：
                tenant：租户名
                pui：分机号码
                number：呼出白名单号码
            默认参数：-
            auther:wxl
            date:2019-12-27
        """
        logging.info("begin add out white number")
        body = {"tenant": tenant, "auctenatMum": pui, "start": 0, "limit": 0}
        out_white_number_api = "http://%s/api/v1/commoncfg/hpui/outWhite?tenant=%s&auctenatMum=%s&start=0&limit=10" % (
        Management_IP, tenant, pui)
        r = requests.get(url=out_white_number_api, headers=self.headers, data=json.dumps(body))
        outwhitenum = ""
        if r.status_code == 200:
            if r.json()["total"] >= 1:
                if r.json()["rows"]:
                    for i in range(r.json()["total"]):
                        outwhitenum += r.json()["rows"][i]["aucAllAddrNum"]
                        outwhitenum += ','
                else:
                    logging.error("query out white number failed，rows为空")
                    return 0
        outwhitenum += str(number)
        body = {"aucTenantInfo": tenant, "aucPui": pui, "aucAllAddrNum": outwhitenum}
        if r.json()["total"] == 0:
            res = requests.put(url=OUT_WHITE % Management_IP, headers=self.headers, data=json.dumps(body))
            logging.info("out white number info: %s" % str(body))
            if res.status_code == 200:
                logging.info("add out white number successful\n")
                return 1
            else:
                logging.error("add out white number failed, response code = %d, error: %s\n" % (r.status_code, r.text))
                return 0
        else:
            res = requests.post(url=OUT_WHITE % Management_IP, headers=self.headers, data=json.dumps(body))
            logging.info("out white number info: %s" % str(body))
            if res.status_code == 200:
                logging.info("add out white number successful\n")
                return 1
            else:
                logging.error("add out white number failed, response code = %d, error: %s\n" % (r.status_code, r.text))
                return 0

    def add_in_white(self, tenant, pui, number):
        """
            新增分机呼入白名单:
            参数：
                tenant：租户名
                pui：分机号码
                number：呼入白名单号码
            默认参数：-
            auther:wxl
            date:2019-12-27
        """
        logging.info("begin add in white number")
        body = {"tenant": tenant, "auctenatMum": pui, "start": 0, "limit": 0}
        in_white_number_api = "http://%s/api/v1/commoncfg/hpui/inWhite?tenant=%s&auctenatMum=%s&start=0&limit=10" % (
            Management_IP, tenant, pui)
        r = requests.get(url=in_white_number_api, headers=self.headers, data=json.dumps(body))
        inwhitenum = ""
        if r.status_code == 200:
            if r.json()["total"] >= 1:
                if r.json()["rows"]:
                    for i in range(r.json()["total"]):
                        inwhitenum += r.json()["rows"][i]["aucAllAddrNum"]
                        inwhitenum += ','
                else:
                    logging.error("query in white number failed，rows为空")
                    return 0
        inwhitenum += str(number)
        body = {"aucTenantInfo": tenant, "aucPui": pui, "aucAllAddrNum": inwhitenum}
        if r.json()["total"] == 0:
            res = requests.put(url=IN_WHITE % Management_IP, headers=self.headers, data=json.dumps(body))
            logging.info("in white number info: %s" % str(body))
            if r.status_code == 200:
                logging.info("add in white number successful\n")
                return 1
            else:
                logging.error("add in white number failed, response code = %d, error: %s\n" % (r.status_code, r.text))
                return 0
        else:
            r = requests.post(url=IN_WHITE % Management_IP, headers=self.headers, data=json.dumps(body))
            logging.info("add in white number info: %s" % str(body))
            if r.status_code == 200:
                logging.info("add in white number successful\n")
                return 1
            else:
                logging.error("add in white number failed, response code = %d, error: %s\n" % (r.status_code, r.text))
                return 0

    def add_in_black(self, tenant, pui, number):
        """
            新增分机呼入黑名单:
            参数：
                tenant：租户名
                pui：分机号码
                number：呼入黑名单号码
            默认参数：-
            auther:wxl
            date:2019-12-27
        """
        logging.info("begin add in black number")
        body = {"tenant": tenant, "auctenatMum": pui, "start": 0, "limit": 0}
        in_black_number_api = "http://%s/api/v1/commoncfg/hpui/inBlack?tenant=%s&auctenatMum=%s&start=0&limit=10" % (
            Management_IP, tenant, pui)
        r = requests.get(url=in_black_number_api, headers=self.headers, data=json.dumps(body))
        inblacknum = ""
        if r.status_code == 200:
            if r.json()["total"] >= 1:
                if r.json()["rows"]:
                    for i in range(r.json()["total"]):
                        inblacknum += r.json()["rows"][i]["aucAllAddrNum"]
                        inblacknum += ','
                else:
                    logging.error("query in black number failed，rows为空")
                    return 0
        inblacknum += str(number)
        body = {"aucTenantInfo": tenant, "aucPui": pui, "aucAllAddrNum": inblacknum}
        if r.json()["total"] == 0:
            res = requests.put(url=IN_BLACK % Management_IP, headers=self.headers, data=json.dumps(body))
            logging.info("in black number info: %s" % str(body))
            if res.status_code == 200:
                logging.info("add in black number successful\n")
                return 1
            else:
                logging.error("add in black number failed, response code = %d, error: %s\n" % (r.status_code, r.text))
                return 0
        else:
            res = requests.post(url=IN_BLACK % Management_IP, headers=self.headers, data=json.dumps(body))
            logging.info("in black number info: %s" % str(body))
            if res.status_code == 200:
                logging.info("add in black number successful\n")
                return 1
            else:
                logging.error("add in black number failed, response code = %d, error: %s\n" % (r.status_code, r.text))
                return 0
# ------------------------------------------- Black_White_Number Method End -------------------------------------------#


if __name__ == '__main__':
    aa = VpbxEmsConfig()
    for i in range(29):
        a = 401+i
        # b = "abcd" + str(a)
        # ofiiceurl = "abc" + str(a) + ".com"
        # t = 2 + i
        # ip = "192.168.10." + str(t)
        aa.add_in_black('autotest1.com', '1001', a)
        #time.sleep(1)




