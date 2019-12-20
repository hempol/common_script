# -*- coding:utf8 -*-

import datetime
import xlrd      #读取表数据
import pymysql as MySQLdb
import paramiko
from xlutils.copy import copy

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
path = "/root/ab.xls"
USER = []
SDNC = []
MANO = []

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
        self.ssh.close()

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

jk = QUERY()
jk.query_user()
jk.query_sdnc()
jk.query_mano()
write_excel_xls_append(0, USER)
write_excel_xls_append(1, SDNC)
write_excel_xls_append(2, MANO)