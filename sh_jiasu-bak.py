# -*- coding: UTF-8 -*-
import xlrd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import time
x_data = ['20190823', '20190828', '20190829', '20190830', '20190902', '20190903', '20190904', '20190905', '20190906', '20190907', '20190908', '20190909', '20190910', '20190911', '20190912', '20190913', '20190914', '20190915', '20190916', '20190917', '20190918']
y_data = [6.6, 6.84, 6.9, 6.91, 7.13, 7.13, 7.03, 7.1, 7.22, 7.23, 7.34, 7.41, 7.43, 7.56, 7.54, 7.57, 7.66, 7.56, 7.61, 7.58, 7.6]
y_data2 = [7.6, 7.84, 7.9, 8.91, 9.13, 0.13, 9.03, 7.1, 9.22, 7.23, 7.34, 7.41, 7.43, 7.56, 7.54, 7.57, 7.66, 7.56, 7.61, 7.58, 7.6]
plt.figure(figsize=(12, 12), dpi=100)

#a = list(range(len(x_data)))
#plt.xticks(a, x_data, rotation=45, fontsize=5)
#print('22222')
# print(ax.get_xticklabels()[::])
# for label in ax.get_xticklabels():
#     label.set_visible(False)
# print(ax.get_xticklabels()[::])
# for label in ax.get_xticklabels():
#     label.set_visible(True)
# print(ax.get_xticklabels()[::])

time.sleep(3)
plt.subplot(111)
plt.plot(x_data,y_data) # 在2x2画布中第一块区域输出图形
plt.plot(x_data,y_data2)
# plt.xticks(['20190823',  '20190903',  '20190908',  '20190913',  '20190918'], rotation=45, fontsize=5)  # 设置x轴刻度
# plt.subplot(222)
# plt.plot(x_data,y_data)    #在2x2画布中第二块区域输出图形
# plt.xticks(['20190823',  '20190903',  '20190908',  '20190913',  '20190918'])  # 设置x轴刻度
# plt.subplot(223)  #在2x2画布中第三块区域输出图形
# plt.plot(x_data,y_data)
# plt.xticks(['20190823',  '20190903',  '20190908',  '20190913',  '20190918'])  # 设置x轴刻度
# plt.subplot(224)  # 在在2x2画布中第四块区域输出图形
# plt.plot(x_data,y_data)
# plt.xticks(x_data[::2])  # 设置x轴刻度
# time.sleep(3)
plt.savefig('d:/fig.png')
