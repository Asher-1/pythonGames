#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@author: Asher
@time:2018/3/8 13:17
'''

import socket

server = socket.socket()
server.bind(('localhost', 8080))
server.listen()

while True:
    conn, addr = server.accept()

    while True:
        data = conn.recv(1024)
        if not data:
            print('the client is lost!!!')
            break
        print('>>>', data.decode())
        data = input('>>>').encode('utf-8')
        conn.send(data)

server.close()