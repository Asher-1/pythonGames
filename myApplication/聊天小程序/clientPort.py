#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@author: Asher
@time:2018/3/8 19:22
'''

import socket

client = socket.socket()
client.connect(('localhost', 8080))

while True:
    data = input('>>>')
    client.send(data.encode('utf-8'))  # data必须为字节序列
    data = client.recv(1024).decode()
    print('>>>', data)


client.close()