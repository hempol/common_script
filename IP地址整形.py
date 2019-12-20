
# -*- coding:utf8 -*-
__author__ = 'lei'

from IPy import IP

def revers_int_ip(ip):
    ip_tmp = ip.split('.')
    ip_tmp.reverse()
    ip_adr_int = IP('.'.join(ip_tmp)).int()
    return ip_adr_int

print(revers_int_ip('22.24.0.4'))
