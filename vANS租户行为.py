# -*- coding:utf8 -*-
__author__ = 'lei'

from IPy import IP
import pymysql as MySQLdb
import time


def generate_ip(ip,number):

    count = 0
    ip_list = []
    ip_s = IP(ip)
    for i in ip_s:
        if IP(i) == IP(ip_s.net()) or IP(i) == IP(ip_s.broadcast()):
            continue
        ip_list.append(str(i))
        count += 1
        if count == number:
            break
    return ip_list


def revers_int_ip(ip):
    ip_tmp = ip.split('.')
    ip_tmp.reverse()
    ip_adr_int = IP('.'.join(ip_tmp)).int()
    return ip_adr_int


def vans_add_user(vansip, number):

    id = 0
    # 打开数据库连接
    db = MySQLdb.connect(vansip, "root", "raisecom@123", "VANS", 23306, charset='utf8')
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    for i in generate_ip('172.163.0.0/16',number):
        id += 1
        ip_adr_int = revers_int_ip(i)
        mysql = "insert into UserInfoTable (cpeIp, userId, userPasswd, popMIp, popPIp) values " \
                "(%d, %s, %s, '1915249711', '4150297701');" % (ip_adr_int, str(id), str(id))
        cursor.execute(mysql)
        print("第 %d 条添加完成。。。" % id)
    db.commit()
    db.close()


def vans_del_user(vansip,number):

    id = 0
    db = MySQLdb.connect(vansip, "root", "raisecom@123", "VANS", 23306, charset='utf8')
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    for i in generate_ip('172.163.0.0/16',number):
        id += 1
        ip_adr_int = revers_int_ip(i)
        mysql = "DELETE FROM UserInfoTable WHERE cpeIp=%d;" % ip_adr_int
        cursor.execute(mysql)
        print ("第 %d 条删除完成。。。" % id)
    db.commit()
    db.close()


def vans_add_usbeinfo(vansip,number):

    curren_time = "2020-04-24 00:00:00"  # 获取当前时间并格式化
    stamp_array = time.strptime(curren_time, '%Y-%m-%d %H:%M:%S')  # 利用strptime()将其转换成时间数组
    stamp = int(time.mktime(stamp_array))
    id = 0
    user = 0
    db = MySQLdb.connect(vansip, "root", "raisecom@123", "VANS", 23306, charset='utf8')
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    for i in generate_ip('172.162.0.0/16',number):
        user += 1
        user_id = 0
        ip_adr_int = revers_int_ip(i)
        for j in generate_ip('192.168.100.0/24',60):
            id += 1
            user_id += 1
            ip_adr_int2 = revers_int_ip(j)
            mysql = "INSERT INTO UsbeTable (cpeIp, hostName, popIp, upFlow, downFlow,protocol,duration,startTime,endTime," \
                    "currentTime,updateTime) VALUES (%d, %d, 1915249711, %d, %d,20480,10000,1556075211,1556075212,%d,'2019-12-05 08:33:55');" % \
                    (ip_adr_int, ip_adr_int2, user, user_id, stamp)
            cursor.execute(mysql)
            #print (mysql)
            print("第 %d 条: 用户 %d 的第 %s 添加完成。。。" % (id, user, user_id))
    db.commit()
    db.close()


def vans_del_usbeinfo(vansip,number):

    id = 0
    db = MySQLdb.connect(vansip, "root", "raisecom@123", "VANS", 23306, charset='utf8')
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    for i in generate_ip('172.162.0.0/16',number):
        id += 1
        ip_adr_int = revers_int_ip(i)
        mysql = "DELETE FROM UsbeTable WHERE cpeIp=%d;" % ip_adr_int
        cursor.execute(mysql)
        print("第 %d 条删除完成。。。" % id)
    db.commit()
    db.close()


if __name__ == "__main__":
    vansip = '192.168.193.37'
    user_count = 4950
    vans_add_user(vansip, user_count)
    vans_add_usbeinfo(vansip, user_count)
    # vans_del_usbeinfo(vansip, user_count)
    # vans_del_user(vansip, user_count)

