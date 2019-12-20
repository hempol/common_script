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
            print(response.status_code, response.text)
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
            #print(response.status_code, response.text)
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

    def enable_cpe(self, firstcpe, endcpe):
        self.firstcpe = firstcpe
        self.endcpe = endcpe
        s_sum = 0
        f_sum = 0
        f_list = ''
        self.enableurl = "http://%s:3000/api/notify/cpestatus" % self.soIp
        for k in range(firstcpe, endcpe + 1):
            logicid = str(1000000 + k)
            body = {"logicId": logicid, "cpeStatus": "enable", "operationType": 0, "area": '10001'}
            response = requests.post(url=self.enableurl, headers=self.headersTmp, data=json.dumps(body))
            time.sleep(2)
            print(self.enableurl)
            print(self.headersTmp)
            print(response.text)
            print(response.status_code)
            if response.status_code == 200:
                s_sum += 1
                print("###### %s' enable SUCCESS ######" % logicid.encode())
            else:
                f_sum += 1
                f_list = f_list + str(k) + ' '
                print("###### %s' enable FAILED ######" % logicid.encode())
        if f_sum:
            title = ["CPE总数", "成功个数", "失败个数", "失败详情"]
            datas = [self.endcpe + 1 - self.firstcpe, s_sum, f_sum, f_list]
            self.sum(title, datas)
        else:
            title = ["CPE总数", "成功个数", "失败个数"]
            datas = [self.endcpe+1-self.firstcpe, s_sum, f_sum]
            self.sum(title, datas)


class SSH:
    # CPE可通性检查及加速业务验证

    def __init__(self, hostname, port, username, password):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(self.hostname, self.port, self.username, self.password)

    def sum(self, title, datas):
        self.tb = PrettyTable(title)
        self.tb.add_row(datas)
        print('')
        print('')
        print("执行结果统计：")
        print(self.tb)
        print('')

    def cpe_connectivity(self, firstcpe, endcpe):
        self.firstcpe = firstcpe
        self.endcpe = endcpe
        s_sum = 0
        f_sum = 0
        f_list = ''
        for k in range(firstcpe, endcpe + 1):
            cpemanageip = 'ping 172.133.%s.1 -c 4' % str(k)
            stdin, stdout, stderr = self.ssh.exec_command(cpemanageip)
            res, err = stdout.read(), stderr.read()
            result = res if res else err
            # print(result)
            if len(re.findall(r'4 received', result.decode())):
                s_sum += 1
                print(("Cpe %s is reachable") % cpemanageip[13:15])
            elif len(re.findall(r'100% packet loss', result.decode())):
                f_sum += 1
                f_list = f_list + str(k) + ' '
                print(("Cpe %s is unreachable") % cpemanageip[13:15])
            else:
                s_sum += 1
                print(("Cpe %s is loss of packets") % cpemanageip[13:15])
        self.ssh.close()
        if f_sum:
            title = ["CPE总数", "成功个数", "失败个数", "失败详情"]
            datas = [self.endcpe + 1 - self.firstcpe, s_sum, f_sum, f_list]
            self.sum(title, datas)
        else:
            title = ["CPE总数", "成功个数", "失败个数"]
            datas = [self.endcpe+1-self.firstcpe, s_sum, f_sum]
            self.sum(title, datas)

    def cpe_acc_connectivity(self, firstcpe, endcpe):
        s_sum = 0
        f_sum = 0
        f_list = ''
        self.firstcpe = firstcpe
        self.endcpe = endcpe
        self.ssh.exec_command('route del -net 45.76.231.0/24')
        for k in range(firstcpe, endcpe + 1):
            routecmd = 'route add -net 45.76.231.0/24 gw 172.133.%s.1' % k
            self.ssh.exec_command("route del -net 45.76.231.0/24")
            self.ssh.exec_command(routecmd)
            time.sleep(2)
            stdin, stdout, stderr = self.ssh.exec_command("wget --timeout=2 --tries=10 "
                                                          "--delete-after http://45.76.231.7/404.html")
            res, err = stdout.read(), stderr.read()
            result = res if res else err
            if len(re.findall(r'100%', result.decode('utf-8'))):
                print(("CPE %s's 加速业务Http get请求成功!" % (k)))
                s_sum += 1
            else:
                print("CPE %s's 加速业务Http get请求失败" % (k))
                f_sum += 1
                f_list = f_list + str(k) + ' '
            self.ssh.exec_command("route del -net 45.76.231.0/24")
        #self.ssh.close()
        if f_sum:
            title = ["CPE总数", "成功个数", "失败个数", "失败详情"]
            datas = [self.endcpe + 1 - self.firstcpe, s_sum, f_sum, f_list]
            self.sum(title, datas)
        else:
            title = ["CPE总数", "成功个数", "失败个数"]
            datas = [self.endcpe+1-self.firstcpe, s_sum, f_sum]
            self.sum(title, datas)

class Manager_cpe:
    # CPE常用配置

    def __init__(self, username=CPE_USERNAME, password=CPE_PASSWORD, port=CPE_PORT):
        self.username = username
        self.password = password
        self.port = port
        self.firstcpe = firstcpe
        self.endcpe = endcpe
        self.cfg_cpe = []
        for k in range(self.firstcpe, self.endcpe + 1):
            self.cfg_cpe.append(('192.168.192.' + str(k)).encode())

    def Telnet(self, ip):
        self.ip = ip
        Tn = telnetlib.Telnet(self.ip, self.port)

        Tn.read_until(b"Username:")
        Tn.write((self.username + "\r").encode())
        Tn.read_until(b"Password:")
        Tn.write(self.password + b"\r")
        Tn.read_until(b"host>")
        Tn.write(b"enable\r")
        Tn.read_until(b"host#")
        return Tn

    def sum_table(self, title, *args):
        self.tb = PrettyTable(title)
        for i in range(len(args[0])):
            line = []
            for j in range(len(args)):
                line.append(args[j][i])
            self.tb.add_row(line)
        print('')
        print('')
        print("执行结果统计：")
        print(self.tb)
        print('')

    def cpe_version_update(self):
        for i in self.cfg_cpe:
            Tn = self.Telnet(i)
            Tn.write(b"copy tftp 192.168.207.101 MSG2200E-8V_SYSTEM_3.20.67_20190517.bin image\r")
            Tn.read_until(b"host#")
            Tn.write(b"diagnose\r")
            Tn.read_until(b"Password:")
            Tn.write(b"zhjrqmwg!\r")
            time.sleep(1)
            Tn.write(b"reboot\r")
            time.sleep(1)
            Tn.close()
            print("CPE %s is upgraded" % str(i))

    def tmp(self):
        for i in self.cfg_cpe:
            Tn = self.Telnet(i)
            Tn.write(b"configure terminal\r")
            Tn.read_until(b"host(config)#")
            Tn.write(b"netconf\r")
            Tn.read_until(b"host(config-netconf)#")
            Tn.write(b"no call-home all\r")
            Tn.read_until(b"host(config-netconf)#")
            Tn.write(b"call-home del sdn_callhome\r")
            Tn.read_until(b"host(config-netconf)#")
            Tn.write(b"call-home add sdn_callhome url 172.160.120.200 port 6666 auth ssh\r")
            Tn.read_until(b"host(config-netconf)#")
            Tn.write(b"call-home sdn_callhome bind pon0.42\r")
            Tn.read_until(b"host(config-netconf)#")
            Tn.write(b"call-home sdn_callhome\r")
            Tn.read_until(b"host(config-netconf)#")
            print(i.decode())
            Tn.close()

    def query_cpe_info(self):
        cpe = []
        management_ip = []
        snat_ip = []
        mac_address = []
        version = []
        acc_bus = []
        netconf_status = []
        title = ['    CPE    ', 'Management IP', 'Snat IP', 'MAC', 'Version', 'Acc Business', 'Netconf Status']
        for i in self.cfg_cpe:
            Tn = self.Telnet(i)
            Tn.write(b"configure terminal\r")
            Tn.read_until(b"host(config)#")
            Tn.write(b"netconf\r")
            Tn.read_until(b"host(config-netconf)#")
            Tn.write(b"show call-home all\r")
            result = str(Tn.read_until(b"host(config-netconf)#"))
            if "closed" in result:
                status = "closed"
            elif "connecting" in result:
                status = "connecting"
            else:
                status = "connected"
            Tn.write(b"end\r")
            Tn.read_until(b"host#")
            Tn.write(b"show version\r")
            echo = str(Tn.read_until(b"Bootrom version"))
            ver = echo[-37:-20]
            Tn.write(b"diagnose\r")
            Tn.read_until(b"Password:")
            Tn.write(b"zhjrqmwg!\r")
            Tn.read_until(b"/ #")
            Tn.write(b"ifconfig pon0\r")
            echo = Tn.read_until(b"/ #")
            mac = re.findall(b'\w\w:\w\w:\w\w:\w\w:\w\w:\w\w', echo)
            Tn.write(b"ifconfig pon0.42\r")
            echo = Tn.read_until(b"/ #")
            manage_ip = re.findall(b'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', echo)
            Tn.write(b"ifconfig vxlan1000\r")
            echo = Tn.read_until(b"/ #")
            vxlan_interface = re.findall(b'RX bytes', echo)
            snatip = re.findall(b'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', echo)
            Tn.write(b"route -n\r")
            echo = Tn.read_until(b"/ #")
            acc_route = re.findall(b'45\.76\.231\.7', echo)
            if vxlan_interface or acc_route:
                acc_bus.append('Y')
            else:
                acc_bus.append('N')
            if snatip:
                snat_ip.append(snatip[0].decode())
            else:
                snat_ip.append(None)
            cpe.append(i[12:14].decode())
            management_ip.append(manage_ip[0].decode())
            mac_address.append(mac[0].lower().decode())
            version.append(ver)
            netconf_status.append(status)
            Tn.close()
            print('.', end=' ')
        self.sum_table(title, cpe, management_ip, snat_ip, mac_address, version, acc_bus, netconf_status)

    def clear_cpe_config_reboot(self):
        for i in self.cfg_cpe:
            Tn = self.Telnet(i)
            # Tn.write(b"configure terminal\r")
            # Tn.read_until(b"host(config)#")
            # Tn.write(b"netconf\r")
            # Tn.read_until(b"host(config-netconf)#")
            # Tn.write(b"erase netconf-config\r")
            # Tn.read_until(b"host(config-netconf)#")
            # Tn.write(b"end\r")
            # Tn.read_until(b"host#")
            Tn.write(b"diagnose\r")
            Tn.read_until(b"Password:")
            Tn.write(b"zhjrqmwg!\r")
            Tn.read_until(b"/ #")
            # Tn.write(b"cd config/\r")
            # Tn.read_until(b"/config #")
            # Tn.write(b"rm syscfg.con\r")
            # Tn.read_until(b"/config #")
            # Tn.write(b"cp syscfg.con.bak syscfg.con\r")
            # Tn.read_until(b"/config #")
            # Tn.write(b"cd /tmp/yuma/\r")
            # Tn.read_until(b"/tmp/yuma #")
            # Tn.write(b'echo "" > startup-cfg.xml\r')
            # Tn.read_until(b"/tmp/yuma #")
            Tn.write(b"reboot\r")
            time.sleep(1)
            Tn.close()
            print("CPE %s config cleared and reboot" % str(i[12:14].decode()))

if __name__ == "__main__":
    firstcpe = 13
    endcpe = 13

    # +++++++++++++++++++加速业务+++++++++++++++++++++++++++++++++#
                                                             
    cfg = Cloud()
    #cfg.add_acc_business(firstcpe, endcpe)
    #cfg.enable_cpe(firstcpe, endcpe)
    cfg.del_acc_business(firstcpe, endcpe)
    # while True:
    #     cfg.del_acc_business(firstcpe, endcpe)
    #     time.sleep(3600)
    #     cfg.add_acc_business(firstcpe, endcpe)
    #     time.sleep(7200)

    # +++++++++++++++++++终端验证+++++++++++++++++++++++++++++++++#

    #t = SSH('172.100.203.22', '9922', 'root', 'admin-00')
    #t.cpe_connectivity(firstcpe, endcpe)
    #t.cpe_acc_connectivity(firstcpe, endcpe)
    #for i in range(10):
        #t.cpe_acc_connectivity(firstcpe, endcpe)
    #t.ssh.close()

    # ++++++++++++++++++++CPE管理+++++++++++++++++++++++++++++++++#

    #mcpe = Manager_cpe()
    #mcpe.cpe_version_update()
    #mcpe.query_cpe_info()
    #mcpe.upload_startup_config()
    #mcpe.clear_cpe_config_reboot()
    #mcpe.tmp()
    
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
