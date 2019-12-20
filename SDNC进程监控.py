# -*- coding:utf8 -*-

import datetime
import xlrd      #读取表数据
import paramiko
from xlutils.copy import copy
# from time import sleep
# import subprocess
# import matplotlib.pyplot as plt
# import random

ip_address = '192.168.193.253'
ssh_username = 'root'
ssh_password = 'raisecom!@#$'
ssh_port = 9922
path = "C:/ab.xls"
logpath = "C:/dfjk.log"
system = []
process = []
pid = []
thread = []
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
    '''查询管理网元信息'''

    def __init__(self):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def exec_command(self, ssh, command):
        stdin, stdout, stderr = ssh.exec_command(command)
        res, err = stdout.read(), stderr.read()
        result = res if res else err
        return result

    def query_process_info(self, name):
        self.name = name
        command_pid= "pgrep -f '%s'" % self.name
        echo = self.exec_command(self.ssh, command_pid).decode().replace("\n","")
        pid.append(echo)
        command_ram = "cat /proc/%s/status | grep VmRSS" % echo
        echo1 = self.exec_command(self.ssh, command_ram).split()
        process_ram = echo1[1]
        process.append(process_ram.decode(encoding='utf-8'))
        command_thread = "cat /proc/%s/status | grep Thread " % echo
        echo2 = self.exec_command(self.ssh, command_thread).split()
        thread.append(echo2[1].decode())

    
    def query(self):
        self.ssh.connect(ip_address, ssh_port, ssh_username, ssh_password)
        # 第一列：日期
        system.append(datetime.datetime.now().strftime("%Y/%m/%d"))
        # 第二列：Memory total
        echo = self.exec_command(self.ssh, "free -m | grep Mem").split( )
        Memory_total = echo[1]
        system.append(Memory_total.decode(encoding='utf-8'))
        # 第三列：Memory used
        Memory_used = echo[2]
        system.append(Memory_used.decode(encoding='utf-8'))
        # 第四列：Memory Usage
        system.append('{:.2%}'.format(int(Memory_used)/int(Memory_total)))
        # 第五列：Disk totle
        echo = self.exec_command(self.ssh, "df -m |awk '{print $2}'").split( )
        echo.pop(0)
        echo = [int(x) for x in echo]
        Disk_totle = sum(echo)
        system.append(str(Disk_totle))
        # 第六列：Disk Usage
        echo = self.exec_command(self.ssh, "df -m |awk '{print $3}'").split()
        echo.pop(0)
        echo = [int(x) for x in echo]
        Disk_Used = sum(echo)
        system.append('{:.2%}'.format(Disk_Used / Disk_totle))

        # system PROCESS RAM USAGE
        # 第一列：日期
        process.append(datetime.datetime.now().strftime("%Y/%m/%d"))
        pid.append(datetime.datetime.now().strftime("%Y/%m/%d"))
        thread.append(datetime.datetime.now().strftime("%Y/%m/%d"))
        for i in process_name:
            self.query_process_info(i)
        self.ssh.close()
        with open(logpath, 'a+') as f:
            f.write(datetime.datetime.now().strftime("%H:%M:%S") + ": system查询结果 " + str(system) +"\n")
            f.write(datetime.datetime.now().strftime("%H:%M:%S") + ": process查询结果 " + str(process) + "\n")
            f.write(datetime.datetime.now().strftime("%H:%M:%S") + ": pid查询结果 " + str(pid) + "\n")
            f.write(datetime.datetime.now().strftime("%H:%M:%S") + ": thread查询结果 " + str(thread) + "\n")


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
            f.write(datetime.datetime.now().strftime("%H:%M:%S") + ": system结果数据写入xls成功" "\n")
    elif sheet_index == 1:
        with open(logpath, 'a+') as f:
            f.write(datetime.datetime.now().strftime("%H:%M:%S") + ": process结果数据写入xls成功" "\n")
    elif sheet_index == 2:
        with open(logpath, 'a+') as f:
            f.write(datetime.datetime.now().strftime("%H:%M:%S") + ": pid结果数据写入xls成功" "\n")
    elif sheet_index == 3:
        with open(logpath, 'a+') as f:
            f.write(datetime.datetime.now().strftime("%H:%M:%S") + ": thread结果数据写入xls成功" "\n")


# def picture_data(path, sheet_name = None, row = None):
#     #获取excel某sheet页面多列的数据，row为列id的数组；注：excel第一列的id是0.
#     data = []
#     workbook = xlrd.open_workbook(path)
#     sheet = workbook.sheet_by_name(sheet_name)
#     for i in row:
#         data.append(sheet.col_values(i))
#     return data
#
#
# def line_color():
#     all_color = ['aqua', 'aquamarine', 'black', 'blue'
#         , 'blueviolet', 'brown', 'burlywood', 'cadetblue', 'chartreuse', 'chocolate', 'coral', 'cornflowerblue'
#         , 'crimson', 'cyan', 'darkblue', 'darkcyan', 'darkgoldenrod', 'darkgray', 'darkgreen', 'darkkhaki', 'darkmagenta'
#         , 'darkolivegreen', 'darkorange', 'darkorchid', 'darkred', 'darksalmon', 'darkseagreen', 'darkslateblue', 'darkslategray'
#         , 'darkturquoise', 'darkviolet', 'deeppink', 'deepskyblue', 'dimgray', 'dodgerblue', 'firebrick', 'forestgreen'
#         , 'fuchsia', 'gainsboro', 'gold', 'goldenrod', 'gray', 'green', 'hotpink', 'indianred'
#         , 'indigo', 'lawngreen', 'lime', 'limegreen', 'magenta', 'maroon', 'mediumaquamarine', 'mediumblue', 'mediumorchid'
#         , 'mediumpurple', 'mediumseagreen', 'mediumslateblue', 'mediumspringgreen', 'mediumturquoise', 'mediumvioletred', 'midnightblue'
#         , 'navy', 'olive', 'olivedrab', 'orange', 'orangered', 'orchid', 'peachpuff', 'peru', 'powderblue'
#         , 'purple', 'red', 'rosybrown', 'royalblue', 'saddlebrown', 'salmon', 'sandybrown', 'seagreen', 'seashell', 'sienna', 'silver', 'skyblue'
#         , 'slateblue', 'slategray', 'springgreen', 'steelblue', 'tan', 'teal', 'tomato', 'turquoise', 'yellow', 'yellowgreen']
#     id = random.randint(0,91)
#     color = all_color[id]
#     all_color.pop(id)
#     return color
#
# def draw_picture():
#     subprocess.run("rm -f /root/*.png", shell=True)
#     plt.figure(figsize=(20, 16), dpi=120)
#     #system数据获取及处理，生成折线图
#     plt.subplot(221)
#     plt.title('system Resources Useage')
#     plt.xlabel('Specific Date')
#     plt.ylabel('Useage Rate - %')
#     system_data = picture_data(path, sheet_name="system", row=[0, 3, 5, 6, 7])
#     system_data[0].pop(0)
#     x_data = [x.replace('/', '')[-6:] for x in system_data[0]]
#     system_data.pop(0)
#     for i in range(len(system_data)):
#         label_name = system_data[i][0]
#         system_data[i].pop(0)
#         y_data = [float(y.replace('%', '')) for y in system_data[i]]
#         plt.plot(x_data, y_data, color=line_color(), label=label_name, linewidth=3)     # 在2x2画布中第一块区域输出图形
#         plt.xticks(x_data[::2], rotation=45, fontsize=10)  # 设置x轴刻度
#     plt.legend()
#     # system数据获取及处理，生成折线图
#     plt.subplot(222)
#     plt.title('MANO Resources Useage')
#     plt.xlabel('Specific Date')
#     plt.ylabel('Useage Rate - %')
#     system_data = picture_data(path, sheet_name="MANO", row=[0, 3, 5, 6, 7, 8, 9])
#     system_data[0].pop(0)
#     x_data = [x.replace('/', '')[-6:] for x in system_data[0]]
#     system_data.pop(0)
#     for i in range(len(system_data)):
#         label_name = system_data[i][0]
#         system_data[i].pop(0)
#         y_data = [float(y.replace('%', '')) for y in system_data[i]]
#         plt.plot(x_data, y_data, color=line_color(), label=label_name, linewidth=3)  # 在2x2画布中第二块区域输出图形
#         plt.xticks(x_data[::2], rotation=45, fontsize=10)  # 设置x轴刻度
#     plt.legend()
#     # VCPE数据获取及处理，生成折线图
#     plt.subplot(223)  # 在2x2画布中第三块区域输出图形
#     plt.title('VCPE Resources Useage')
#     plt.xlabel('Specific Date')
#     plt.ylabel('Useage Rate - %')
#     system_data = picture_data(path, sheet_name="VCPE", row=[0, 3, 5, 6])
#     system_data[0].pop(0)
#     x_data = [x.replace('/', '')[-6:] for x in system_data[0]]
#     system_data.pop(0)
#     for i in range(len(system_data)):
#         label_name = system_data[i][0]
#         system_data[i].pop(0)
#         y_data = [float(y.replace('%', '')) for y in system_data[i]]
#         plt.plot(x_data, y_data, color=line_color(), label=label_name, linewidth=3)  # 在2x2画布中第二块区域输出图形
#         plt.xticks(x_data[::2], rotation=45, fontsize=10)  # 设置x轴刻度
#     plt.legend()
#     # VANS数据获取及处理，生成折线图
#     plt.subplot(224)  # 在2x2画布中第四块区域输出图形
#     plt.title('VANS Resources Useage')
#     plt.xlabel('Specific Date')
#     plt.ylabel('Useage Rate - %')
#     system_data = picture_data(path, sheet_name="VANS", row=[0, 3, 5, 6, 7, 8, 9, 10])
#     system_data[0].pop(0)
#     x_data = [x.replace('/', '')[-6:] for x in system_data[0]]
#     system_data.pop(0)
#     for i in range(len(system_data)):
#         label_name = system_data[i][0]
#         system_data[i].pop(0)
#         y_data = [float(y.replace('%', '')) for y in system_data[i]]
#         plt.plot(x_data, y_data, color=line_color(), label=label_name, linewidth=3)  # 在2x2画布中第二块区域输出图形
#         plt.xticks(x_data[::2], rotation=45, fontsize=10)  # 设置x轴刻度
#     plt.legend()
#     sleep(3)
#     plt.savefig("/root/" + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + ".png", dpi=120)
#     with open(logpath, 'a+') as f:
#         f.write(datetime.datetime.now().strftime("%H:%M:%S") + ": 表图处理、生成成功""\n""\n")

if __name__ == '__main__':
    with open(logpath, 'a+') as f:
        f.write("\n""==============" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "===============""\n")
    jk = QUERY()
    jk.query()
    print()
    write_excel_xls_append(0, system)
    write_excel_xls_append(1, process)
    write_excel_xls_append(2, pid)
    write_excel_xls_append(3, thread)
    #draw_picture()
