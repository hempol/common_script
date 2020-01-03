# -*- coding:utf-8 -*-

import easygui as g
import os
import time
import paramiko
import threading
import configparser
from prettytable import PrettyTable
import requests
import simplejson as json
import re

USERNAME = 'root'
PASSWORD = 'raisecom@2017'

# ##EMS API###
VCODE_API = "http://%s/api/v1/uiframe/icode"
TOKEN_API = "http://%s/api/v1/uiframe/login"
SET_SHELL_API = 'http://%s/api/v1/commoncfg/shell/set'
GET_SHELL_API = 'http://%s/api/v1/commoncfg/shell/getResult?unitID=101'

BSU_RUN_LOG = "/usr/bsu/bsu_prj/H1/oams/runlog/"
BSU_CALL_LOG = "/usr/bsu/bsu_prj/H1/oams/calllog/"
SPU_RUN_LOG = "/usr/spu/spu_prj/H1/oams/runlog/"
DMU_RUN_LOG = "/usr/dmu/dmu_prj/H1/oams/runlog/"
DEST_DIR = r"C:\Users\Administrator\Desktop"
INI_FILE = r"C:\Users\Public\Documents\vpbx.ini"
RESOURCE_COMMANDS = {'shell_imp_as_show_ccb': '', 'shell_mrf_mrfc_show_ccb': '', 'imp_spms_uac_show': '',
                     'imp_spms_uas_show': '', 'imp_spms_uacs_show': '', 'cscf_comm_instance_reg_show': '',
                     'cscf_comm_instance_call_show': '', 'imp_spm_msg_context_busy_count': ''}

try:

    config = configparser.ConfigParser()
    if os.path.exists(INI_FILE) is False:
        config["VPBX"] = {'IP': '172.102.201.24',
                             'PORT': 9922,
                             'USERNAME': 'root',
                             'PASSWD': 'raisecom!@#$'
                             }
        with open(INI_FILE, 'w') as f:
            config.write(f)
    config.read(INI_FILE)
    msg = "请填写VPBX信息：\n\n" \
          "【* IP地址】：   vpbx的管理地址\n" \
          "【* 端口】：       vpbx的SSH端口，默认是9922\n" \
          "【* 用户名】：   vpbx的SSH用户名，默认是root\n" \
          "【* 密码】：       vpbx的SSH密码，默认是raisecom!@#$"
    title = "VPBX测试诊断工具 v1.1.3                      author：wxl"
    fieldNames = ["    *IP地址 ", "    *端口 ", "    *用户名 ", "    *密码 "]
    fieldValues = []
    ret = g.multenterbox(msg, title, fieldNames, values=[config['VPBX']['IP'], config['VPBX']['PORT'], config['VPBX']['USERNAME'], config['VPBX']['PASSWD']])
    if ret == None:
        raise ValueError('cancel')
    else:
        IP = str(ret[0])
        config.set('VPBX', 'IP', IP)
        PORT = int(ret[1])
        config.set('VPBX', 'PORT', str(PORT))
        USERNAME = str(ret[2])
        config.set('VPBX', 'USERNAME', USERNAME)
        PASSWD = ret[3]
        config.set('VPBX', 'PASSWD', PASSWD)
        with open(INI_FILE, 'w') as f:
            config.write(f)


    class VpbxEmsConfig():
        """VPX网管EMS配置的基础类，包含了各业务配置项的配置方法，供自动化配置调用"""

        def __init__(self, Management_IP=IP):
            self.managementIp = Management_IP
            self.userName = USERNAME
            self.vcodeApi = VCODE_API % self.managementIp
            self.tokenApi = TOKEN_API % self.managementIp
            self.vcode = requests.get(url=self.vcodeApi).text
            self.headersTmp = {'Content-Type': 'application/x-www-form-urlencoded'}
            body = {"username": self.userName, "domains": [], "tenantId": "null", "userType": "1",
                    "password": "RCMfGAQa/XeKc+jCmYQDHg==", "isEncypted": "true", "vcode": self.vcode}
            r = requests.post(url=self.tokenApi, headers=self.headersTmp, data=json.dumps(body))
            self.scode = re.findall(r'scode=(.*?);', r.headers['Set-Cookie'])
            self.headers = {'Content-Type': 'application/json', 'Cookie': 'scode= ' + self.scode[0]}

        def qu(self, command):
            set_api = SET_SHELL_API % self.managementIp
            get_api = GET_SHELL_API % self.managementIp
            response_text = ''
            resource = ''
            resource_count = 0
            body = {"unitID": "101", "aucShCmd": command}
            res = requests.post(url=set_api, headers=self.headers, data=json.dumps(body))
            if res.status_code == 200:
                while True:
                    r = requests.get(url=get_api, headers=self.headers)
                    if r.status_code == 200:
                        try:
                            response_text += r.json()['rows'][0]['aucShCmdRsp']
                            if r.json()['rows'][0]['isEnd'] == 1:
                                break
                        except Exception as e:
                            resource_count = 'request3 failed'
                            break
                    else:
                        resource_count = 'request2 failed'
                        break
                print(response_text)
                if command == 'shell_imp_as_show_ccb':
                    resource = re.findall(r'ALL CCBID NUM IS\[(\d*)\]?', response_text)
                elif command == 'shell_mrf_mrfc_show_ccb':
                    resource = re.findall(r'MRFC ALL CCB\[(\d*)\]?', response_text)
                elif command == 'imp_spm_msg_context_busy_count':
                    resource = re.findall(r'message contexts,(\d*) message contexts busy!?', response_text)
                else:
                    resource = re.findall(r'there are \[(\d*)\]?', response_text)
                if resource:
                    resource_count = int(resource[0])
                    if resource_count > 0:
                        with open('%s.log' % command, 'a') as f:
                            f.write(response_text)
                else:
                    resource_count = 'query failed'
            else:
                resource_count = 'request1 failed'

            return resource_count

    class SshConnect:

        def __init__(self, ip=IP, port=PORT, username=USERNAME, password=PASSWD):
            self.ip = ip
            self.port = port
            self.username = username
            self.password = password

        def ssh_client(self):
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.ip, self.port, self.username, self.password)
            return ssh

        def ssh_exec_command(self, command):
            stdin, stdout, stderr = self.ssh_client().exec_command(command)
            self.ssh_client().close()
            return stdout

        def sftp_client(self):
            t = paramiko.Transport(sock=(self.ip, self.port))
            t.connect(username=self.username, password=self.password)
            sftp = paramiko.SFTPClient.from_transport(t)
            return sftp

        def sftp_download(self, remote_path, local_path):
            self.sftp_client().get(remote_path, local_path)
            self.sftp_client().close()


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

    def sum_table_normal(title, *args):
        tb = PrettyTable(title)
        for i in range(len(args)):
            tb.add_row(args[i])
        return tb

    def sum_table(title, *args):
        tb = PrettyTable(title)
        for i in range(len(args[0])):
            line = []
            for j in range(len(args)):
                line.append(args[j][i])
            tb.add_row(line)
        return tb

    def all_process(resource, ssh):
        FILE_NAME = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        os.chdir(DEST_DIR)
        if os.path.exists("log") is False:
            os.makedirs("log")
        os.chdir(DEST_DIR + '\\' + 'log')
        os.chdir(DEST_DIR + '\\' + 'log')
        os.makedirs(FILE_NAME)
        os.chdir(DEST_DIR + '\\' + 'log' + '\\' + FILE_NAME)
        my_thread(ssh.ssh_exec_command, (("cd %s;tar zcvf BSU_runlog.tar.gz runlog.log" % BSU_RUN_LOG,),
                                         ("cd %s;tar zcvf BSU_calllog.tar.gz rlog.log" % BSU_CALL_LOG,),
                                         ("cd %s;tar zcvf SPU_runlog.tar.gz runlog.log" % SPU_RUN_LOG,),
                                         ("cd %s;tar zcvf DMU_runlog.tar.gz runlog.log" % DMU_RUN_LOG,)))
        core_title = ['   Core File   ', 'Size', 'Creat Time']
        core_list = ssh.ssh_exec_command(
            "ls -alth /data/corefile | grep core | awk '{print $9}'").read().decode().split()
        core_size_list = ssh.ssh_exec_command(
            "ls -alth /data/corefile | grep core | awk '{print $5}'").read().decode().split()
        core_time_list = ssh.ssh_exec_command("ls -alth --time-style '+%Y/%m/%d_%H:%M:%S' /data/corefile | grep core |"
                                              " awk '{print $6}'").read().decode().split()
        core = sum_table(core_title, core_list, core_size_list, core_time_list)
        with open('result.log', 'w') as f:
            f.write('1.VPBX系统中存在 %s 个core文件，core文件信息:\n\n' % len(core_list))
            if len(core_list):
                f.write(core.get_string() + '\n')
                f.write('\n\n')
            else:
                f.write(sum_table_normal(core_title, ['None（not exist）', '-', '-']).get_string() + '\n\n')
        with open('result.log', 'a') as f:
            f.write('2.VPBX语音资源占用信息：\n\n                  AS、MRF资源占用信息' + '\n')

        for key, value in RESOURCE_COMMANDS.items():
            RESOURCE_COMMANDS[key] = resource.qu(key)

        as_title = [' shell_imp_as_show_ccb ', ' shell_mrf_mrfc_show_ccb ']
        as_resource_count_list = []
        as_resource_count_list.append(RESOURCE_COMMANDS['shell_imp_as_show_ccb'])
        as_resource_count_list.append(RESOURCE_COMMANDS['shell_mrf_mrfc_show_ccb'])
        with open('result.log', 'a') as f:
            f.write(sum_table_normal(as_title, as_resource_count_list).get_string() + '\n\n')

        cscf_title = ['cscf_comm_instance_reg_show', 'cscf_comm_instance_call_show']
        cscf_resource_count_list = []
        cscf_resource_count_list.append(RESOURCE_COMMANDS['cscf_comm_instance_reg_show'])
        cscf_resource_count_list.append(RESOURCE_COMMANDS['cscf_comm_instance_call_show'])
        with open('result.log', 'a') as f:
            f.write('                      CSCF资源占用信息' + '\n')
            f.write(sum_table_normal(cscf_title, cscf_resource_count_list).get_string() + '\n\n')

        spms_title = ['imp_spms_uac_show', 'imp_spms_uas_show', 'imp_spms_uacs_show', 'spm_context_busy_count']
        spms_resource_count_list = []
        spms_resource_count_list.append(RESOURCE_COMMANDS['imp_spms_uac_show'])
        spms_resource_count_list.append(RESOURCE_COMMANDS['imp_spms_uas_show'])
        spms_resource_count_list.append(RESOURCE_COMMANDS['imp_spms_uacs_show'])
        spms_resource_count_list.append(RESOURCE_COMMANDS['imp_spm_msg_context_busy_count'])
        with open('result.log', 'a') as f:
            f.write('                                 SPMS资源占用信息' + '\n')
            f.write(sum_table_normal(spms_title, spms_resource_count_list).get_string() + '\n\n')

        with open('result.log', 'a') as f:
            f.write('3.VPBX日志下载信息：' + '\n\n')
            f.write('  BSU  runlog: runlog最新日志下载完成\n')
            f.write('  BSU calllog: calllog最新日志下载完成\n')
            f.write('  SPU calllog: calllog最新日志下载完成\n')
            f.write('  DMU calllog: calllog最新日志下载完成\n\n')

        my_thread(ssh.sftp_download, (
        (BSU_RUN_LOG + 'BSU_runlog.tar.gz', DEST_DIR + '\\' + 'log' + '\\' + FILE_NAME + '\\' + 'BSU_runlog.tar.gz'),
        (BSU_CALL_LOG + 'BSU_calllog.tar.gz', DEST_DIR + '\\' + 'log' + '\\' + FILE_NAME + '\\' + 'BSU_calllog.tar.gz'),
        (SPU_RUN_LOG + 'SPU_runlog.tar.gz', DEST_DIR + '\\' + 'log' + '\\' + FILE_NAME + '\\' + 'SPU_runlog.tar.gz'),
        (DMU_RUN_LOG + 'DMU_runlog.tar.gz', DEST_DIR + '\\' + 'log' + '\\' + FILE_NAME + '\\' + 'DMU_runlog.tar.gz')))
        my_thread(ssh.ssh_exec_command,
                  (("rm -f %s/BSU_runlog.tar.gz" % BSU_RUN_LOG,), ("rm -f %s/BSU_calllog.tar.gz" % BSU_CALL_LOG,),
                   ("rm -f %s/SPU_runlog.tar.gz" % SPU_RUN_LOG,), ("rm -f %s/DMU_runlog.tar.gz" % DMU_RUN_LOG,)))
        r = g.textbox(msg='一、VPBX的CORE文件、语音资源占用及各网元日志：\n\n\n  查询执行时间:  ' +
                      time.strftime("%Y.%m.%d %H:%M:%S",
                                    time.localtime()) + '\n\n  本地存储路径：' + ' ' + DEST_DIR + '\\' + 'log' +
                      '\\' + FILE_NAME, title='VPBX测试诊断结果',
                  text=open(DEST_DIR + '\\' + 'log' + '\\' + FILE_NAME + '\\result.log', 'r'))
        return r
    if __name__ == "__main__":

        resource = VpbxEmsConfig()
        ssh = SshConnect()
        while True:
            if all_process(resource, ssh) is None:
                break

except Exception as e:
    if e.__str__() == 'cancel':
        pass
    else:
        title = g.msgbox(msg=e, title="错误信息", ok_button="关闭")
