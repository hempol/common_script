# -*- coding:utf8 -*-

import datetime
import xlrd      #读取表数据
import pymysql as MySQLdb
import paramiko
from xlutils.copy import copy
from time import sleep
import subprocess
import matplotlib.pyplot as plt
import random

sdnc_address = '15.192.131.83'
sdnc_ssh_name = 'root'
sdnc_ssh_password = 'Raisecom@123'
sdnc_ssh_port = 22
sdnc_db_user = 'root'
sdnc_db_password = 'raisecom@123'
sdnc_db_port = 23306
mano_address = '15.192.131.82'
mano_ssh_name = 'root'
mano_ssh_password = 'Raisecom@123'
mano_ssh_port = 22
vans_address = '15.192.131.93'
vans_ssh_name = 'root'
vans_ssh_password = 'raisecom!@#$'
vans_ssh_port = 9922
vcpe_address = '15.192.131.94'
vcpe_ssh_name = 'raisecom'
vcpe_ssh_password = 'raisecom'
vcpe_ssh_port = 22
path = "/root/ab.xls"
logpath = "/var/log/dfjk.log"
USER = []
SDNC = []
MANO = []
VANS = []
VCPE = []
SDNC_PROCESS = []
process_name = ['org.apache.hadoop.hbase.master.HMaster start',
                '/netconf/lib/boot/org.apache.karaf.main',
                'ems/lib/boot/org.osgi.core-6.0.0.jar org.apache.karaf.main.Main',
                'pm_ext/lib/boot/org.osgi.core-6.0.0.jar org.apache.karaf.main.Main',
                'inventory/lib/boot/org.osgi.core-6.0.0.jar org.apache.karaf.main.Main',
                'mysql.sock --port=23306',
                'webappServer/lib/boot/org.osgi.core-6.0.0.jar org.apache.karaf.main.Main',
                'alarm_ext/lib/boot/org.osgi.core-6.0.0.jar org.apache.karaf.main.Main',
                'service_common/lib/boot/org.osgi.core-6.0.0.jar org.apache.karaf.main.Main',
                'nbi/lib/boot/org.osgi.core-6.0.0.jar org.apache.karaf.main.Main',
                'sdncgop/lib/boot/org.osgi.core-6.0.0.jar org.apache.karaf.main.Main',
                '/usr/local/msp/comp/service/so/policy-mgmt',
                '/usr/local/msp/comp/service/so/karaf/bin',
                '/usr/local/msp/comp/service/so/workerorder/bin',
                '/usr/local/msp/comp/service/so/business-mgmt',
                '/usr/local/msp/comp/service/so/resource-mgmt',
                '/usr/local/msp/comp/service/so/commonInterface/bin',
                '/usr/local/msp/runtime/jre-8u131-linux-x64/bin/java -jar alarm.jar',
                '/usr/local/msp/comp/service/redis/redis-4.0.1/redis-server',
                'node /usr/local/msp/comp/service/webapp/bin/www',
                '/usr/local/msp/comp/service/webapp/bin/resource_sync',
                '/usr/local/msp/comp/service/elasticsearch/elasticsearch-7.0.0/lib/',
                'sysagent.jar',
                '/usr/local/msp/comp/service/kafka/bin/../logs/zookeeper-gc.log',
                '/usr/local/msp/comp/service/kafka/bin/../logs/kafkaServer-gc.log',
                'apigateway.jar',
                '/usr/sbin/ntpd -u ntp:ntp',
                '/usr/sbin/vsftpd /etc/vsftpd/vsftpd.conf',
                '/var/log/rabbitmq/rabbit@localhost_upgrade.log',
                'configcenter.jar',
                'configcenter_ems.jar',
                'pmmng-service.jar',
                'pmcollect-service.jar',
                'sysmng_daemon.py',
                'sysmng_entry.py',
                'logs-service.jar']

class QUERY:
    '查询管理网元信息'

    def __init__(self):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def exec_command(self, ssh, command):
        stdin, stdout, stderr = ssh.exec_command(command)
        res, err = stdout.read(), stderr.read()
        result = res if res else err
        return result

    def query_process_ram(self, name):
        self.name = name
        command_pid= "pgrep -f '%s'" % self.name
        echo = self.exec_command(self.ssh, command_pid).decode().replace("\n","")
        command_ram = "cat /proc/%s/status | grep VmRSS" % echo
        echo = self.exec_command(self.ssh, command_ram).split()
        process_ram = echo[1]
        SDNC_PROCESS.append(process_ram.decode(encoding='utf-8'))

    def query_user(self):
        # 第一列：日期
        USER.append(datetime.datetime.now().strftime("%Y/%m/%d"))
        # 第二列：用户数
        db = MySQLdb.connect(sdnc_address, sdnc_db_user, sdnc_db_password, "so_order", sdnc_db_port, charset='utf8')
        # 使用cursor()方法获取操作游标
        cursor = db.cursor()
        mysql = "SELECT COUNT(*) FROM %s" % 'worker_order_business'
        cursor.execute(mysql)
        user_number = cursor.fetchone()
        USER.append(str(user_number[0]))
        db.close()
        with open(logpath, 'a+') as f:
            f.write(datetime.datetime.now().strftime("%H:%M:%S") + ": USER查询结果 " + str(USER) +"\n")

    def query_sdnc(self):
        self.ssh.connect(sdnc_address, sdnc_ssh_port, sdnc_ssh_name, sdnc_ssh_password)
        # 第一列：日期
        SDNC.append(datetime.datetime.now().strftime("%Y/%m/%d"))
        # 第二列：Memory total
        echo = self.exec_command(self.ssh, "free -m | grep Mem").split( )
        Memory_total = echo[1]
        SDNC.append(Memory_total.decode(encoding='utf-8'))
        # 第三列：Memory used
        Memory_used = echo[2]
        SDNC.append(Memory_used.decode(encoding='utf-8'))
        # 第四列：Memory Usage
        SDNC.append('{:.2%}'.format(int(Memory_used)/int(Memory_total)))
        # 第五列：Disk totle
        echo = self.exec_command(self.ssh, "df -m |awk '{print $2}'").split( )
        echo.pop(0)
        echo = [int(x) for x in echo]
        Disk_totle = sum(echo)
        SDNC.append(str(Disk_totle))
        # 第六列：Disk Usage
        echo = self.exec_command(self.ssh, "df -m |awk '{print $3}'").split()
        echo.pop(0)
        echo = [int(x) for x in echo]
        Disk_Used = sum(echo)
        SDNC.append('{:.2%}'.format(Disk_Used / Disk_totle))
        # 第七列：Log Usage
        echo = self.exec_command(self.ssh, "df -h | grep /dev/mapper/centos-var_log").split()
        Log_Usage = echo[4]
        SDNC.append(Log_Usage.decode(encoding='utf-8'))
        # 第七列：Backup Db Usage
        echo = self.exec_command(self.ssh, "df -h | grep /dev/mapper/centos-root").split()
        Backup_Db_Usage = echo[4]
        SDNC.append(Backup_Db_Usage.decode(encoding='utf-8'))
        # SDNC PROCESS RAM USAGE
        # 第一列：日期
        SDNC_PROCESS.append(datetime.datetime.now().strftime("%Y/%m/%d"))
        for i in process_name:
            self.query_process_ram(i)
        self.ssh.close()
        with open(logpath, 'a+') as f:
            f.write(datetime.datetime.now().strftime("%H:%M:%S") + ": SDNC查询结果 " + str(SDNC) +"\n")
        with open(logpath, 'a+') as f:
            f.write(datetime.datetime.now().strftime("%H:%M:%S") + ": SDNC PROCESS RAM查询结果 " + str(SDNC_PROCESS) +"\n")

    def query_mano(self):
        self.ssh.connect(mano_address, mano_ssh_port, mano_ssh_name, mano_ssh_password)
        # 第一列：日期
        MANO.append(datetime.datetime.now().strftime("%Y/%m/%d"))
        # 第二列：Memory total
        echo = self.exec_command(self.ssh, "free -m | grep Mem").split()
        Memory_total = echo[1]
        MANO.append(Memory_total.decode(encoding='utf-8'))
        # 第三列：Memory used
        Memory_used = echo[2]
        MANO.append(Memory_used.decode(encoding='utf-8'))
        # 第四列：Memory Usage
        MANO.append('{:.2%}'.format(int(Memory_used) / int(Memory_total)))
        # 第五列：Disk totle
        echo = self.exec_command(self.ssh, "df -m |awk '{print $2}'").split()
        echo.pop(0)
        echo = [int(x) for x in echo]
        Disk_totle = sum(echo)
        MANO.append(str(Disk_totle))
        # 第六列：Disk Usage
        echo = self.exec_command(self.ssh, "df -m |awk '{print $3}'").split()
        echo.pop(0)
        echo = [int(x) for x in echo]
        Disk_Used = sum(echo)
        MANO.append('{:.2%}'.format(Disk_Used / Disk_totle))
        # 第七列：Log Usage
        echo = self.exec_command(self.ssh, "df -h | grep /dev/mapper/centos-var").split()
        Log_Usage = echo[4]
        MANO.append(Log_Usage.decode(encoding='utf-8'))
        # 第七列：Backup Usage
        echo = self.exec_command(self.ssh, "df -h | grep /dev/mapper/centos-data").split()
        Backup_Usage = echo[4]
        MANO.append(Backup_Usage.decode(encoding='utf-8'))
        # 第八列：Db Usage
        echo = self.exec_command(self.ssh, "df -h | grep /dev/mapper/centos-log").split()
        Db_Usage = echo[4]
        MANO.append(Db_Usage.decode(encoding='utf-8'))
        # 第八列：Root Usage
        echo = self.exec_command(self.ssh, "df -h | grep /dev/mapper/centos-root").split()
        Root_Usage = echo[4]
        MANO.append(Root_Usage.decode(encoding='utf-8'))
        self.ssh.close()
        with open(logpath, 'a+') as f:
            f.write(datetime.datetime.now().strftime("%H:%M:%S") + ": MANO查询结果 " + str(MANO) +"\n")

    def query_vans(self):
        self.ssh.connect(vans_address, vans_ssh_port, vans_ssh_name, vans_ssh_password)
        # 第一列：日期
        VANS.append(datetime.datetime.now().strftime("%Y/%m/%d"))
        # 第二列：Memory total
        echo = self.exec_command(self.ssh, "free -m | grep Mem").split()
        Memory_total = echo[1]
        VANS.append(Memory_total.decode(encoding='utf-8'))
        # 第三列：Memory used
        Memory_used = echo[2]
        VANS.append(Memory_used.decode(encoding='utf-8'))
        # 第四列：Memory Usage
        VANS.append('{:.2%}'.format(int(Memory_used) / int(Memory_total)))
        # 第五列：Disk totle
        echo = self.exec_command(self.ssh, "df -m |awk '{print $2}'").split()
        echo.pop(0)
        echo = [int(x) for x in echo]
        Disk_totle = sum(echo)
        VANS.append(str(Disk_totle))
        # 第六列：Disk Usage
        echo = self.exec_command(self.ssh, "df -m |awk '{print $3}'").split()
        echo.pop(0)
        echo = [int(x) for x in echo]
        Disk_Used = sum(echo)
        VANS.append('{:.2%}'.format(Disk_Used / Disk_totle))
        # 第七列：Log Usage
        echo = self.exec_command(self.ssh, "df -h | grep /dev/mapper/centos-var_log").split()
        Log_Usage = echo[4]
        VANS.append(Log_Usage.decode(encoding='utf-8'))
        # 第八列：Backup Usage
        echo = self.exec_command(self.ssh, "df -h | grep /dev/mapper/centos-data").split()
        Backup_Usage = echo[4]
        VANS.append(Backup_Usage.decode(encoding='utf-8'))
        # 第九列：Db Usage
        echo = self.exec_command(self.ssh, "df -h | grep /dev/mapper/centos-opt").split()
        Db_Usage = echo[4]
        VANS.append(Db_Usage.decode(encoding='utf-8'))
        # 第十列：Db Usage
        echo = self.exec_command(self.ssh, "df -h | grep /dev/mapper/centos-home").split()
        Db_Usage = echo[4]
        VANS.append(Db_Usage.decode(encoding='utf-8'))
        # 第十一列：Root Usage
        echo = self.exec_command(self.ssh, "df -h | grep /dev/mapper/centos-root").split()
        Root_Usage = echo[4]
        VANS.append(Root_Usage.decode(encoding='utf-8'))
        self.ssh.close()
        with open(logpath, 'a+') as f:
            f.write(datetime.datetime.now().strftime("%H:%M:%S") + ": VANS查询结果 " + str(VANS) +"\n")

    def query_vcpe(self):
        self.ssh.connect(vcpe_address, vcpe_ssh_port, vcpe_ssh_name, vcpe_ssh_password)
        # 第一列：日期
        VCPE.append(datetime.datetime.now().strftime("%Y/%m/%d"))
        # 第二列：Memory total
        echo = self.exec_command(self.ssh, "free -m | grep Mem").split()
        Memory_total = echo[1]
        VCPE.append(Memory_total.decode(encoding='utf-8'))
        # 第三列：Memory used
        Memory_used = echo[2]
        VCPE.append(Memory_used.decode(encoding='utf-8'))
        # 第四列：Memory Usage
        VCPE.append('{:.2%}'.format(int(Memory_used) / int(Memory_total)))
        # 第五列：Disk totle
        echo = self.exec_command(self.ssh, "df -m |awk '{print $2}'").split()
        echo.pop(0)
        echo = [int(x) for x in echo]
        Disk_totle = sum(echo)
        VCPE.append(str(Disk_totle))
        # 第六列：Disk Usage
        echo = self.exec_command(self.ssh, "df -m |awk '{print $3}'").split()
        echo.pop(0)
        echo = [int(x) for x in echo]
        Disk_Used = sum(echo)
        VCPE.append('{:.2%}'.format(Disk_Used / Disk_totle))
        # 第七列：Root Usage
        echo = self.exec_command(self.ssh, "df -h | grep /dev/mapper/centos-root").split()
        Root_Usage = echo[4]
        VCPE.append(Root_Usage.decode(encoding='utf-8'))
        self.ssh.close()
        with open(logpath, 'a+') as f:
            f.write(datetime.datetime.now().strftime("%H:%M:%S") + ": VCPE查询结果 " + str(VCPE) +"\n")

def write_excel_xls_append(sheet_index, value):
    workbook = xlrd.open_workbook(path)           #打开文件，获取excel文件的workbook（工作簿）对象
    sheet = workbook.sheet_by_index(sheet_index)  #获取sheet对象
    rows = sheet.nrows                            # 获取该表总行数
    newworkbook = copy(workbook)
    sheet = newworkbook.get_sheet(sheet_index)    #获取sheet对象
    sheet.write(rows, sheet_index, value)
    for i in range(len(value)):
        sheet.write(rows, i, value[i])
    newworkbook.save(path)
    if sheet_index == 0:
        with open(logpath, 'a+') as f:
            f.write(datetime.datetime.now().strftime("%H:%M:%S") + ": USER结果数据写入xls成功" "\n")
    elif sheet_index == 1:
        with open(logpath, 'a+') as f:
            f.write(datetime.datetime.now().strftime("%H:%M:%S") + ": MANO结果数据写入xls成功" "\n")
    elif sheet_index == 2:
        with open(logpath, 'a+') as f:
            f.write(datetime.datetime.now().strftime("%H:%M:%S") + ": SDNC结果数据写入xls成功" "\n")
    elif sheet_index == 3:
        with open(logpath, 'a+') as f:
            f.write(datetime.datetime.now().strftime("%H:%M:%S") + ": SDNC PROCESS RAM结果数据写入xls成功" "\n")
    elif sheet_index == 4:
        with open(logpath, 'a+') as f:
            f.write(datetime.datetime.now().strftime("%H:%M:%S") + ": VANS结果数据写入xls成功" "\n")
    elif sheet_index == 5:
        with open(logpath, 'a+') as f:
            f.write(datetime.datetime.now().strftime("%H:%M:%S") + ": VCPE结果数据写入xls成功" "\n")

def connectVPN():
    subprocess.run("echo 'd dfvpn' > /var/run/xl2tpd/l2tp-control", shell=True)
    sleep(5)
    subprocess.run("route del -net 15.192.131.0/24 gw 192.168.5.1", shell=True)
    sleep(20)
    subprocess.check_call("echo 'c dfvpn' > /var/run/xl2tpd/l2tp-control", shell=True)
    sleep(60)
    if  subprocess.getoutput('/usr/sbin/ifconfig').find("ppp") == -1:
        with open(logpath, 'a+') as f:
            f.write(datetime.datetime.now().strftime("%H:%M:%S") + ": L2tp拨号失败""\n")
        raise Exception('L2tp拨号失败')
    else:
        with open(logpath, 'a+') as f:
            f.write(datetime.datetime.now().strftime("%H:%M:%S") + ": L2tp拨号成功""\n")
        subprocess.check_call("/usr/sbin/route add -net 15.192.131.0/24 gw 192.168.5.1", shell=True)
    if  subprocess.getoutput('/usr/sbin/route -n').find("15.192.131.0") == -1:
        with open(logpath, 'a+') as f:
            f.write(datetime.datetime.now().strftime("%H:%M:%S") + ": 路由添加失败，未查询到路由""\n")
        raise Exception('路由添加失败，未查询到路由')
    else:
        with open(logpath, 'a+') as f:
            f.write(datetime.datetime.now().strftime("%H:%M:%S") + ": 目的路由添加成功""\n")
    if  subprocess.getoutput('/usr/bin/ping 15.192.131.82 -c 4').find("64 bytes from 15.192.131.82: icmp_seq=") == -1:
        with open(logpath, 'a+') as f:
            f.write(datetime.datetime.now().strftime("%H:%M:%S") + ": 目的网络不可达""\n")
        raise Exception('目的网络不可达')
    else:
        with open(logpath, 'a+') as f:
            f.write(datetime.datetime.now().strftime("%H:%M:%S") + ": 目的网络可达""\n")
    return 1
def disconnectVPN():
    subprocess.run("echo 'd dfvpn' > /var/run/xl2tpd/l2tp-control", shell=True)
    sleep(15)
    subprocess.run("/usr/sbin/route del -net 15.192.131.0/24 gw 172.160.130.1", shell=True)
    if  subprocess.getoutput('/usr/sbin/ifconfig').find("ppp") == -1:
        with open(logpath, 'a+') as f:
            f.write(datetime.datetime.now().strftime("%H:%M:%S") + ": L2tp连接断开成功""\n")
    else:
        with open(logpath, 'a+') as f:
            f.write(datetime.datetime.now().strftime("%H:%M:%S") + ": L2tp连接断开失败""\n")
        raise Exception('L2tp隧道删除连接失败')
    if  subprocess.getoutput('/usr/sbin/route -n').find("15.192.131.0") == -1:
        with open(logpath, 'a+') as f:
            f.write(datetime.datetime.now().strftime("%H:%M:%S") + ": 目的路由删除成功""\n")
    else:
        with open(logpath, 'a+') as f:
            f.write(datetime.datetime.now().strftime("%H:%M:%S") + ": 目的路由删除失败""\n""\n")
        raise Exception('目的路由删除失败')
    return 1

def picture_data(path, sheet_name = None, row = None):
    #获取excel某sheet页面多列的数据，row为列id的数组；注：excel第一列的id是0.
    data = []
    workbook = xlrd.open_workbook(path)
    sheet = workbook.sheet_by_name(sheet_name)
    for i in row:
        data.append(sheet.col_values(i))
    return data

def line_color():
    all_color = ['aqua','aquamarine','black','blue'
        ,'blueviolet','brown','burlywood','cadetblue','chartreuse','chocolate','coral','cornflowerblue'
        ,'crimson','cyan','darkblue','darkcyan','darkgoldenrod','darkgray','darkgreen','darkkhaki','darkmagenta'
        ,'darkolivegreen','darkorange','darkorchid','darkred','darksalmon','darkseagreen','darkslateblue','darkslategray'
        ,'darkturquoise','darkviolet','deeppink','deepskyblue','dimgray','dodgerblue','firebrick','forestgreen'
        ,'fuchsia','gainsboro','gold','goldenrod','gray','green','hotpink','indianred'
        ,'indigo','lawngreen','lime','limegreen','magenta','maroon','mediumaquamarine','mediumblue','mediumorchid'
        ,'mediumpurple','mediumseagreen','mediumslateblue','mediumspringgreen','mediumturquoise','mediumvioletred','midnightblue'
        ,'navy','olive','olivedrab','orange','orangered','orchid','peachpuff','peru','powderblue'
        ,'purple','red','rosybrown','royalblue','saddlebrown','salmon','sandybrown','seagreen','seashell','sienna','silver','skyblue'
        ,'slateblue','slategray','springgreen','steelblue','tan','teal','tomato','turquoise','yellow','yellowgreen']
    id = random.randint(0,91)
    color = all_color[id]
    all_color.pop(id)
    return color

def draw_picture():
    subprocess.run("rm -f /root/*.png", shell=True)
    plt.figure(figsize=(20, 16), dpi=120)
    #SDNC数据获取及处理，生成折线图
    plt.subplot(221)
    plt.title('SDNC Resources Useage')
    plt.xlabel('Specific Date')
    plt.ylabel('Useage Rate - %')
    sdnc_data = picture_data(path, sheet_name="SDNC", row=[0, 3, 5, 6, 7])
    sdnc_data[0].pop(0)
    x_data = [x.replace('/', '')[-6:] for x in sdnc_data[0]]
    sdnc_data.pop(0)
    for i in range(len(sdnc_data)):
        label_name = sdnc_data[i][0]
        sdnc_data[i].pop(0)
        y_data = [float(y.replace('%', '')) for y in sdnc_data[i]]
        plt.plot(x_data, y_data, color=line_color(), label=label_name, linewidth=3)     # 在2x2画布中第一块区域输出图形
        plt.xticks(x_data[::2], rotation=45, fontsize=10)  # 设置x轴刻度
    plt.legend()
    # SDNC数据获取及处理，生成折线图
    plt.subplot(222)
    plt.title('MANO Resources Useage')
    plt.xlabel('Specific Date')
    plt.ylabel('Useage Rate - %')
    sdnc_data = picture_data(path, sheet_name="MANO", row=[0, 3, 5, 6, 7, 8, 9])
    sdnc_data[0].pop(0)
    x_data = [x.replace('/', '')[-6:] for x in sdnc_data[0]]
    sdnc_data.pop(0)
    for i in range(len(sdnc_data)):
        label_name = sdnc_data[i][0]
        sdnc_data[i].pop(0)
        y_data = [float(y.replace('%', '')) for y in sdnc_data[i]]
        plt.plot(x_data, y_data, color=line_color(), label=label_name, linewidth=3)  # 在2x2画布中第二块区域输出图形
        plt.xticks(x_data[::2], rotation=45, fontsize=10)  # 设置x轴刻度
    plt.legend()
    # VCPE数据获取及处理，生成折线图
    plt.subplot(223)  # 在2x2画布中第三块区域输出图形
    plt.title('VCPE Resources Useage')
    plt.xlabel('Specific Date')
    plt.ylabel('Useage Rate - %')
    sdnc_data = picture_data(path, sheet_name="VCPE", row=[0, 3, 5, 6])
    sdnc_data[0].pop(0)
    x_data = [x.replace('/', '')[-6:] for x in sdnc_data[0]]
    sdnc_data.pop(0)
    for i in range(len(sdnc_data)):
        label_name = sdnc_data[i][0]
        sdnc_data[i].pop(0)
        y_data = [float(y.replace('%', '')) for y in sdnc_data[i]]
        plt.plot(x_data, y_data, color=line_color(), label=label_name, linewidth=3)  # 在2x2画布中第二块区域输出图形
        plt.xticks(x_data[::2], rotation=45, fontsize=10)  # 设置x轴刻度
    plt.legend()
    # VANS数据获取及处理，生成折线图
    plt.subplot(224)  # 在2x2画布中第四块区域输出图形
    plt.title('VANS Resources Useage')
    plt.xlabel('Specific Date')
    plt.ylabel('Useage Rate - %')
    sdnc_data = picture_data(path, sheet_name="VANS", row=[0, 3, 5, 6, 7, 8, 9, 10])
    sdnc_data[0].pop(0)
    x_data = [x.replace('/', '')[-6:] for x in sdnc_data[0]]
    sdnc_data.pop(0)
    for i in range(len(sdnc_data)):
        label_name = sdnc_data[i][0]
        sdnc_data[i].pop(0)
        y_data = [float(y.replace('%', '')) for y in sdnc_data[i]]
        plt.plot(x_data, y_data, color=line_color(), label=label_name, linewidth=3)  # 在2x2画布中第二块区域输出图形
        plt.xticks(x_data[::2], rotation=45, fontsize=10)  # 设置x轴刻度
    plt.legend()
    sleep(3)
    plt.savefig("/root/" + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + ".png", dpi=120)
    with open(logpath, 'a+') as f:
        f.write(datetime.datetime.now().strftime("%H:%M:%S") + ": 表图处理、生成成功""\n""\n")

if __name__ == '__main__':
    with open(logpath, 'a+') as f:
        f.write("\n""==============" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "===============""\n")
    if connectVPN():
        jk = QUERY()
        jk.query_user()
        jk.query_mano()
        jk.query_sdnc()
        jk.query_vans()
        jk.query_vcpe()
        write_excel_xls_append(0, USER)
        write_excel_xls_append(1, MANO)
        write_excel_xls_append(2, SDNC)
        write_excel_xls_append(3, SDNC_PROCESS)
        write_excel_xls_append(4, VANS)
        write_excel_xls_append(5, VCPE)
    disconnectVPN()
    draw_picture()
