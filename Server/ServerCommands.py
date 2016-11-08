# -*- coding: utf-8 -*-
import datetime
import json
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Random import random

from SecureConnection import *
from Server.Database import Database


class Commands:
    def __init__(self, conn, login, key):
        self.conn = conn
        self.login = login
        self.key = key
        self.database = Database()

    def ExecuteComand(self, comand):
        args = comand.split(" ")[1:]
        comand = comand.split(" ")[0]
        # upload filename
        if comand == "upload":
            self.receiveDocumentFromClient(args[0])
        # download filename
        elif comand == "download":
            self.sendDocumentToClient(args[0])
        # delete filename
        elif comand == "delete":
            self.deleteDocument(args[0])
        # sign filename
        elif comand == "sign":
            self.signDocument(args[0])
        # verify filename
        elif comand == "verify":
            self.verifyDocument(args[0])
        # documents
        elif comand == "documents":
            self.availableDocuments()
        # users
        elif comand == "users":
            self.users()
        # change user document right
        elif comand == "change":
            self.change(args[0], args[1], args[2])
        else:
            print("Unknown command")

    def change(self, user, filename, right):
        code, response = self.database.changeRight(self.login, filename, right, user)
        j = json.dumps({"code": code, "response": response})
        send(self.conn,
             j.encode(),
             self.key)

    def users(self):
        j = json.dumps(self.database.users)
        send(self.conn,
             j.encode(),
             self.key)

    def availableDocuments(self):
        avDocsList = self.database.availableDocumentsList(self.login)
        j = json.dumps(avDocsList)
        send(self.conn,
             j.encode(),
             self.key)

    def verifyDocument(self, filename):
        if filename in self.database.availableDocumentsList(self.login):
            sign = self.database.getSign(filename)
            if sign != "-":
                # print(sign)
                j = json.dumps({"code": 0, "sign": sign})
                send(self.conn,
                     j.encode(),
                     self.key)
                send_file(self.conn, self.key, "storage/files/" + filename)
                send_file(self.conn, self.key, "storage/public/" +
                          self.database.getOwner(filename) + ".pem")
            else:
                j = json.dumps({"code": 1, "response":
                    "Document is not signed"})
                send(self.conn,
                     j.encode(),
                     self.key)
        else:
            j = json.dumps({"code": 1, "response":
                "You haven't access to this document"})
            send(self.conn,
                 j.encode(),
                 self.key)

    def signDocument(self, filename):
        if self.database.isUserOrFileExist(self.login, filename)[0] == 0:
            if self.database.isUserOwnerOfDocument(self.login, filename)[0] == 0:
                if self.database.isDocumentSigned(self.login, filename)[0] == 0:
                    buffer = open("storage/files/" + filename, "rb").read()
                    hash = SHA256.new(buffer).digest()
                    f = open('storage/private/' + self.login + '.pem', 'r')
                    key = RSA.importKey(f.read())
                    k = random.StrongRandom().randint(1, key.q - 1)
                    sig = key.sign(hash, k)
                    signature = str(sig)
                    self.database.signDocument(self.login, filename, signature)
                    j = json.dumps({"code": 0, "response":
                        "You signed this document"})
                    send(self.conn,
                         j.encode(),
                         self.key)
                else:
                    j = json.dumps({"code": 1, "response":
                        "You can't resign document"})
                    send(self.conn,
                         j.encode(),
                         self.key)
            else:
                j = json.dumps({"code": 1, "response":
                    "You're not owner of this document"})
                send(self.conn,
                     j.encode(),
                     self.key)
        else:
            j = json.dumps({"code": 1, "response":
                "User or file doesn's exist"})
            send(self.conn,
                 j.encode(),
                 self.key)

    def deleteDocument(self, filename):
        code, response = self.database.deleteDocument(filename, self.login)
        j = json.dumps({"code": code, "response": response})
        send(self.conn,
             j.encode(),
             self.key)

    def receiveDocumentFromClient(self, filename):
        code, response = self.database.addDocument(filename, self.login)
        j = json.dumps({"code": code, "response": response})
        send(self.conn,
             j.encode(),
             self.key)
        if code == 0:
            filename = receive_file(self.conn, self.key, dir="storage/files/")

    def sendDocumentToClient(self, filename):
        code = self.database.isDocumentAvailable(self.login, filename)
        if code == 0:
            j = json.dumps({"code": code, "response": "OK"})
            send(self.conn,
                 j.encode(),
                 self.key)
            send_file(self.conn, self.key, "storage/files/" + filename)
        else:
            j = json.dumps({"code": code, "response":
                "You haven't enough rights or file doesn't exists"})
            send(self.conn,
                 j.encode(),
                 self.key)


# главная функция ожидания команды
def GetComand(conn, addr, login, key):
    c = Commands(conn, login, key)
    while True:
        comand = receive(conn, key, crop=True).decode()
        print(str(datetime.datetime.now()), addr, login, "#:", comand)
        if comand == "exit" or comand == "":
            break
        c.ExecuteComand(comand)
    return
