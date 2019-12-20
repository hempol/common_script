# -*- coding:utf8 -*-

import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import parseaddr, formataddr
import smtplib
import time
import datetime
import pymysql
import re

#代码页加入以下这个
from requests.packages.urllib3.exceptions import InsecureRequestWarning
# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

req_s = 0   # 访问加速目标网站成功次数
req_f = 0   # 访问加速目标网站失败次数
sustag1 = 0 # 访问非加速网络失败计数
sustag2 = 0 # 访问加速目标网站2成功次数（https）
mailtag = 0 # 发送恢复邮件标志
accelerateurl = 'http://45.76.231.7/404.html'
interneturl = "https://www.raisecom.com/"
accelerateurl2 = "https://www.virginia.edu"

def formatAddr(s):  # 格式化邮件地址
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


def sendmail(content='tz'):
    smtp_server = 'smtp.qq.com'
    from_mail = '233087887@qq.com'
    mail_pass = 'rvozsjeofkrdcaja'
    to_mail = ['wangxiaolei@raisecom.com']
    # 构造一个MIMEMultipart对象代表邮件本身
    msg = MIMEMultipart()
    # Header对中文进行转码
    msg['From'] = formatAddr('王小雷 <%s>' % from_mail)
    msg['To'] = ','.join(to_mail)
    if content == 'tz':
        msg['Subject'] = Header('监控通知！ 西安接入上海电信加速业务监测结果', 'utf-8')
        print('-------------------已发送通知邮件-------------------')
    elif content == 'gj':
        msg['Subject'] = Header('监控告警！ 西安接入上海电信加速业务中断...', 'utf-8')
        print('-------------------已发送告警邮件-------------------')
    elif content == 'hf':
        msg['Subject'] = Header('监控通知！ 西安接入上海电信加速业务恢复正常', 'utf-8')
        print('-------------------已发送业务恢复邮件-------------------')
    msg.attach(MIMEText(mailbody(content), 'html', 'utf-8'))
    try:
        s = smtplib.SMTP()
        s.connect(smtp_server, "25")
        s.login(from_mail, mail_pass)
        s.sendmail(from_mail, to_mail, msg.as_string())  # as_string()把MIMEText对象变成str
        s.quit()
    except smtplib.SMTPException as e:
        print ("Error: %s" % e)   # 发送邮件失败


def mailbody(type):
    if type == 'gj':
        body = """
            <html>
            <head>
            <style type="text/css">
            h1 {color: red}
            p {color: black}
            </style>
            </head>
            <body>
            <h1>加速业务监控告警！</h1>
            <p>西安政企网关CPE接入上海电信智能网掣业务平台，于%s出现加速业务中断，请排查解决！</p>
            </body>
            </html>
            """ % time.strftime("%Y-%m-%d %X", time.localtime())
        return body
    if type == 'hf':
        body = """
            <html>
            <head>
            <style type="text/css">
            h1 {color: green}
            p {color: black}
            </style>
            </head>
            <body>
            <h1>业务恢复！</h1>
            <p>西安政企网关CPE接入上海电信智能网掣业务平台，加速业务于%s恢复！</p>
            </body>
            </html>
            """ % time.strftime("%Y-%m-%d %X", time.localtime())
        return body
    if type == "tz":
        num = 0
        s = []
        for i in range(1, 11):
            r = mysqloperation('select', date=(datetime.datetime.now()+datetime.timedelta(days=-i)).strftime("%Y%m%d"), table='summary')
            num += 1
            s.append(str(num))
            if r == None:
                s.append('%s' % str((datetime.datetime.now()+datetime.timedelta(days=-i)).strftime("%Y%m%d")))
                s.append("0")
                s.append("0")
                s.append("0.00%")
                s.append("0")
            else:
                for j in range(0, 3):
                    s.append(str(r[j]))
                if int(r[1]) == 0:
                    s.append("0.00%")
                else:
                    rate = (format(float(float(r[1]))/(float(r[1])+float(r[2])), '.4f'))
                    s_rate = "%.2f%%" % (float(rate)*100)
                    s.append(s_rate)
                s.append(str(r[3]))
        body = """
        <html>
        <head>
        <style type="text/css">
        h1 {color: blue}
        p {color: black}
        thead {color:green}
        tbody {color:black;height:50px}
        tfoot {color:red}
        </style>
        </head>
        <body>
        <h1 align="left">西安政企网关CPE接入上海电信智能网掣业务平台监测结果</h1>
        <p>----------------------------------------------------------------------------------------------------------------------------------------</p>
        <p>近10日加速业务监测结果：</p>
        <table width="80%" border="2">
        <colgroup span="2" align="left"></colgroup>
        <colgroup align="right" style="color:#0000FF;"></colgroup>
        <tr>
        <th>序号</th>
        <th>日期</th>
        <th>加速业务成功次数</th>
        <th>加速业务失败次数</th>
        <th>成功率</th>
        <th>加速业务中断次数</th>
        </tr>
        <tr>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        </tr>
        <tr>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        </tr>
        <tr>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        </tr>
        <tr>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        </tr>
        <tr>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        </tr>
        <tr>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        </tr>
        <tr>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        </tr>
        <tr>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        </tr>
        <tr>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        </tr>
        <tr>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        <td align="center">xyz</td>
        </tr>
        </table>
        <p style="color:blue">注:访问加速业务连续失败10次，每次超时时长10秒，则判定为一次加速业务中断，触发一次业务中断告警。</p>
        <p>----------------------------------------------------------------------------------------------------------------------------------------</p>
        </body>
        </html>
        """
        for k in range(0, 60):
            body = body.replace("xyz", s[k], 1)
        return body


def mysqloperation(Method, date=None, key=None, value=None, key1=None, value1=None, table=None, key2=None,
                   value2=None, key3=None, value3=None, key4=None, value4=None):    # mysql数据库操作
    insert_sql = ''
    if key != None and key1 != None and key2 != None and key3 != None and key4 != None:
        insert_sql = "insert into %s (%s,%s,%s,%s,%s) values (%s,'%s',%s,'%s','%s')" % (table, key, key1, key2, key3, key4, value, value1, value2 , value3, value4)
    elif key != None and key1 != None and key2 != None and key3 != None:
        insert_sql = "insert into %s (%s,%s,%s,%s) values (%s,'%s',%s,'%s')" % (table, key, key1, key2, key3, value, value1, value2 , value3)
    elif key != None and key1 != None and key2 != None:
        insert_sql = "insert into %s (%s,%s,%s) values (%s,%s,%s)" % (table, key, key1, key2, value, value1, value2)
    elif key != None and key1 != None:
        insert_sql = "insert into %s (%s,%s) values (%s,%s)" % (table, key, key1, value, value1)
    elif key1 == None:
        insert_sql = "insert into %s set %s =%s" % (table, key, value)
    select_sql = "select * from %s where date =%s" % (table, date)
    update_sql = "update %s set %s=%s where %s=%s" % (table, key, value, key1, date)
    delete_sql = "delete from %s where date=%s" % (table, date)
    # 打开数据库连接
    db = pymysql.connect("127.0.0.1", "root", "Raisecom@123", "wdx", charset='utf8')
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    if Method == 'select':
        try:
            # 执行sql语句
            cursor.execute(select_sql)
            data = cursor.fetchone()
            # 提交到数据库执行
            db.commit()
            return data
        except:
            # Rollback in case there is any error
            db.rollback()
    elif Method == 'update':
        try:
            # 执行sql语句
            cursor.execute(update_sql)
            # 提交到数据库执行
            db.commit()
        except:
            # Rollback in case there is any error
            db.rollback()
    elif Method == 'insert':
        try:
            # 执行sql语句
            cursor.execute(insert_sql)
            # 提交到数据库执行
            db.commit()
        except:
            # Rollback in case there is any error
            db.rollback()
    elif Method == 'delete':
        try:
            # 执行sql语句
            cursor.execute(delete_sql)
            # 提交到数据库执行
            db.commit()
        except:
            # Rollback in case there is any error
            db.rollback()
    # 关闭数据库连接
    db.close()


def prikeyjudge(t0):
    if mysqloperation('select', date=t0, table='summary') == None:
        sendmail()
        mysqloperation('insert', value=t0, table='summary', key='date')
        return 1    # 新一天
    else:
        return 0    # 今天


def internetprobe(url):
    global sustag1
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            dat = time.strftime("%Y%m%d", time.localtime())
            tim = str(time.strftime("%X", time.localtime()))
            mysqloperation('insert', table='faillog', key='date', key1='time', key2='req_success', key3='url', value=dat, value1=tim, value2=1, value3=url)
            print (('%s : 访问 raisecom.com 成功') % time.strftime("%Y-%m-%d %X", time.localtime()))
        else:
            dat = time.strftime("%Y%m%d", time.localtime())
            tim = time.strftime("%X", time.localtime())
            mysqloperation('insert', table='faillog', key='date', key1='time', key2='req_fail', key3='url', value=dat, value1=tim, value2=1, value3=url)
            print (('%s : 访问 raisecom.com 失败，网络可达....') % time.strftime("%Y-%m-%d %X", time.localtime()))
        sustag1 += 1
    except Exception as e:
        error = re.findall("Connection aborted|Timeout|NewConnectionError", str(e))
        if error == []:
            error.append('unkown error')
        dat = time.strftime("%Y%m%d", time.localtime())
        tim = time.strftime("%X", time.localtime())
        mysqloperation('insert', table='faillog', key='date', key1='time', key2='req_fail', key3='url', key4='fail_reason', value=dat, value1=tim, value2=1, value3=url, value4=error[0])
        print (('%s : 访问 raisecom.com 失败！') % (time.strftime("%Y-%m-%d %X", time.localtime())))

def internationalprobe(url):
    global sustag2
    try:
        response = requests.get(url, timeout=10, verify=False)
        if response.status_code == 200:
            dat = time.strftime("%Y%m%d", time.localtime())
            tim = str(time.strftime("%X", time.localtime()))
            mysqloperation('insert', table='faillog', key='date', key1='time', key2='req_success', key3='url', value=dat, value1=tim, value2=1, value3=url)
            print (('%s : 访问 virginia.edu 成功') % time.strftime("%Y-%m-%d %X", time.localtime()))
        else:
            dat = time.strftime("%Y%m%d", time.localtime())
            tim = time.strftime("%X", time.localtime())
            mysqloperation('insert', table='faillog', key='date', key1='time', key2='req_fail', key3='url', value=dat, value1=tim, value2=1, value3=url)
            print (('%s : 访问 virginia.edu 失败，网络可达....') % time.strftime("%Y-%m-%d %X", time.localtime()))
        sustag2 += 1
    except Exception as e:
        error = re.findall("Connection aborted|Timeout|NewConnectionError", str(e))
        if error == []:
            error.append('unkown error')
        dat = time.strftime("%Y%m%d", time.localtime())
        tim = time.strftime("%X", time.localtime())
        mysqloperation('insert', table='faillog', key='date', key1='time', key2='req_fail', key3='url', key4='fail_reason', value=dat, value1=tim, value2=1, value3=url, value4=error[0])
        print (('%s : 访问 virginia.edu 失败！') % time.strftime("%Y-%m-%d %X", time.localtime()))

global response

while True:
    try:
        t0 = datetime.datetime.now().strftime("%Y%m%d")
        if prikeyjudge(t0) == 1:
            req_s = 0
            req_f = 0
        response = requests.get(accelerateurl, timeout=10)
        time.sleep(10)
        if response.status_code == 200:
            req_s += 1
            mysqloperation('update', date=t0, table='summary', key='req_success', key1='date',
                           value=mysqloperation('select', date=t0, table='summary')[1]+1)
            print (('%s : 第 %s 次加速业务Http get请求执行成功') % (time.strftime("%Y-%m-%d %X", time.localtime()), req_s))
    except Exception as e:
        error = re.findall("Connection aborted|Timeout|NewConnectionError", str(e))
        if error == []:
            error.append('unkown error')
        i = 0
        req_f += 1
        t0 = datetime.datetime.now().strftime("%Y%m%d")
        if prikeyjudge(t0) == 1:
            req_s = 0
            req_f = 0
        mysqloperation('update', date=t0, table='summary', key='req_fail', key1='date',
                       value=mysqloperation('select', date=t0, table='summary')[2]+1)
        dat = time.strftime("%Y%m%d", time.localtime())
        tim = time.strftime("%X", time.localtime())
        mysqloperation('insert', table='faillog', key='date', key1='time', key2='req_fail', key3='url',
                       key4='fail_reason', value=dat, value1=tim, value2=1, value3=accelerateurl, value4=error[0])
        print (('%s : 加速业务第 %s 次请求超时...........') % (time.strftime("%Y-%m-%d %X", time.localtime()),'1'))
        internetprobe(interneturl)
        internationalprobe(accelerateurl2)
        while True:
            try:
                response = requests.get(accelerateurl, timeout=10)
            except Exception as e:
                error = re.findall("Connection aborted|Timeout|NewConnectionError", str(e))
                if error == []:
                    error.append('unkown error')
                time.sleep(10)
                req_f += 1
                i += 1
                print (('%s : 加速业务第 %s 次请求超时...........!') % (time.strftime("%Y-%m-%d %X", time.localtime()),i+1))
                t0 = datetime.datetime.now().strftime("%Y%m%d")
                if prikeyjudge(t0) == 1:
                    req_s = 0
                    req_f = 0
                mysqloperation('update', date=t0, table='summary', key='req_fail', key1='date',
                               value=mysqloperation('select', date=t0, table='summary')[2]+1)
                dat = time.strftime("%Y%m%d", time.localtime())
                tim = time.strftime("%X", time.localtime())
                mysqloperation('insert', table='faillog', key='date', key1='time', key2='req_fail',
                               key3='url', key4='fail_reason', value=dat, value1=tim, value2=1,
                               value3=accelerateurl, value4=error[0])
                internetprobe(interneturl)
                internationalprobe(accelerateurl2)
                if i == 9 and sustag1 > 1 and sustag2 < 1:
                    print (('监控警告 : 加速业务于 %s 出现中断...........') % (time.strftime("%Y-%m-%d %X", time.localtime())))
                    t0 = datetime.datetime.now().strftime("%Y%m%d")
                    if prikeyjudge(t0) == 1:
                        req_s = 0
                        req_f = 0
                    mysqloperation('update', date=t0, table='summary', key='business_fail', key1='date',
                                   value=mysqloperation('select', date=t0, table='summary')[3]+1)
                    sendmail(content='gj')
                    mailtag += 1
            else:
                if response.status_code == 200:
                    req_s += 1
                    sustag1 = 0
                    sustag2 = 0
                    print (('%s : 第 %s 次加速业务Http get请求执行成功!') % (time.strftime("%Y-%m-%d %X", time.localtime()), req_s))
                    if mailtag == 1:
                        sendmail(content='hf')
                        mailtag -= 1
                    t0 = datetime.datetime.now().strftime("%Y%m%d")
                    if prikeyjudge(t0) == 1:
                        req_s = 0
                        req_f = 0
                    mysqloperation('update', date=t0, table='summary', key='req_success', key1='date',
                                   value=mysqloperation('select', date=t0, table='summary')[1]+1)
                    break

