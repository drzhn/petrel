# -*- coding: utf-8 -*-
from SecureConnection import *
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Random import random

# upload
def upload(comand,clientSocket,md5pass):
    filename = comand.split(" ")[1]
    send(clientSocket,comand.encode(),md5pass)
    j = receive(clientSocket,md5pass).decode()
    j = json.loads(j)
    print(j["response"])
    if j["code"] == 0:
        send_file(clientSocket,md5pass,filename)

# download
def download(comand,clientSocket,md5pass):
    send(clientSocket,comand.encode(),md5pass)
    j = receive(clientSocket,md5pass).decode()
    j = json.loads(j)
    # print(j["response"])
    if j["code"] == 0:
        receive_file(clientSocket,md5pass)
        print("File downloaded")
    else:
        print(j["response"])

# delete document
def delete(comand,clientSocket,md5pass):
    send(clientSocket,comand.encode(),md5pass)
    j = receive(clientSocket,md5pass).decode()
    j = json.loads(j)
    print(j["response"])

# sign document
def signDoc(comand, clientSocket, md5pass):
    send(clientSocket,comand.encode(),md5pass)
    j = receive(clientSocket,md5pass).decode()
    j = json.loads(j)
    print(j["response"])

# verify document
def verify(comand,clientSocket, login, md5pass):
    filename = comand.split(" ")[1]
    send(clientSocket,comand.encode(),md5pass)
    j = receive(clientSocket,md5pass).decode()
    j = json.loads(j)
    if j["code"] == 1:
        print(j["response"])
    else:
        # print(j["sign"])
        sign = j["sign"]
        # print(sign)
        signature_tuple = eval(sign)
        receive_file(clientSocket, md5pass)
        pubPem = receive_file(clientSocket, md5pass)
        buffer = open(filename, "rb").read()
        hash = SHA256.new(buffer).digest()
        f = open(pubPem, 'r')
        public_key = RSA.importKey(f.read())
        if public_key.verify(hash, signature_tuple):
            print("Correct signature")
        else:
            print("Incorrect signature")

# documents
def documents(comand,clientSocket,md5pass):
    send(clientSocket,comand.encode(),md5pass)
    j = receive(clientSocket,md5pass).decode()
    j = json.loads(j)
    for i in j:
        print(i)

# users
def users(comand,clientSocket,md5pass):
    send(clientSocket,comand.encode(),md5pass)
    j = receive(clientSocket,md5pass).decode()
    j = json.loads(j)
    for i in j:
        print(i)

# change user document right
def change(comand,clientSocket,md5pass):
    send(clientSocket, comand.encode(), md5pass)
    j = receive(clientSocket, md5pass).decode()
    j = json.loads(j)
    print(j["response"])

def executeCommands(comand,clientSocket,login, md5pass):
    c = comand.split(" ")[0]
    if c == "upload":
        upload(comand,clientSocket,md5pass)
    if c == "download":
        download(comand,clientSocket,md5pass)
    if c == "delete":
        delete(comand, clientSocket, md5pass)
    if c == "sign":
        signDoc(comand, clientSocket, md5pass)
    if c == "verify":
        verify(comand, clientSocket, login, md5pass)
    if c == "documents":
        documents(comand, clientSocket, md5pass)
    if c == "users":
        users(comand, clientSocket, md5pass)
    if c == "change":
        change(comand, clientSocket, md5pass)