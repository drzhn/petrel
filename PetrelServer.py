# -*- coding: utf-8 -*-
import socket
import threading
from Server.Login import Login
from Server.ServerCommands import GetComand
from SecureConnection import *


def client(conn, addr):
    login, md5pass = Login(conn)
    if login != "":
        send(conn, b"Welcome to Petrel, " + login.encode() + b"!", md5pass)
        # receive_file(conn,md5pass)
        GetComand(conn, addr, login, key=md5pass)
        print("client exited")
    else:
        # send(conn, b"Unknown login or password", md5pass)
        print("Unknown user")
        return


serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind(("127.0.0.1", 10000))
serversocket.listen(10)
addrThreads = {}

while True:
    conn, addr = serversocket.accept()
    serversocket.settimeout(None)
    addrThreads[addr] = threading.Thread(target=client, args=(conn, addr,))
    addrThreads[addr].start()

for k in addrThreads.keys():
    addrThreads[k].join()

serversocket.close()
