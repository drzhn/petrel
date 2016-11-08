# -*- coding: utf-8 -*-
"""
скрипт для работы с базой данных
добавление, удаление, изменение прав документа
добавление, удаление пользователя
"""
import sqlite3
import datetime

from Crypto.Hash import MD5
from Crypto.PublicKey import RSA


class Database:
    users = []
    documents = []

    def __init__(self):
        self.con = sqlite3.connect('Petrel.db')
        self.cur = self.con.cursor()
        self.cur.execute('SELECT * FROM users')
        for row in self.cur:
            self.users.append(row[1])
        self.cur.execute('SELECT * FROM files')
        for row in self.cur:
            self.documents.append(row[1])

    def addDocument(self, filename, owner):
        self.documents.append(filename)
        # посчитаем, сколько документов имеют такое имя
        self.cur.execute("SELECT filename FROM files "
                         "WHERE filename = ?;", [filename])
        count = 0
        for row in self.cur:
            count += 1
        # print(count)
        # создадим добавим документ только в том случае, если
        # документа с именем нет в системе
        if count == 0:
            self.cur.execute("INSERT INTO files "
                             "(filename, owner, sign, date)"
                             "VALUES (?,?,?,?)",
                             [filename, owner, "-", str(datetime.datetime.now())])
            for user in self.users:
                if user != owner:
                    # для всех остальных будет право N
                    self.cur.execute("INSERT INTO hru "
                                     "(filename, user, right)"
                                     "VALUES (?,?,?);",
                                     [filename, user, "n"])
                    self.con.commit()
                else:
                    # для пользователя будет право O
                    self.cur.execute("INSERT INTO hru "
                                     "(filename, user, right)"
                                     "VALUES (?,?,?);",
                                     [filename, user, "o"])
                    self.con.commit()
            return (0, "File " + filename + " added")
        else:
            return (1, "Document with name " + filename +
                    " currently exists in system")

    # удаление файла с именем filename при сеансе currentUser
    def deleteDocument(self, filename, currentUser):
        self.cur.execute("SELECT owner FROM files "
                         "WHERE filename = ?;",
                         [filename])
        fileOwner = ""
        for row in self.cur:
            fileOwner = row[0]
        if fileOwner == currentUser:
            self.cur.execute("DELETE FROM files WHERE filename = ?",
                             [filename])
            self.cur.execute("DELETE FROM hru WHERE filename = ?",
                             [filename])
            self.con.commit()
            # TODO добавить скрипт физического удаления файла
            return 0, "File deleted"
        else:
            return 1, "You're not owner, you can't delete this document"

    def isDocumentAvailable(self, currentUser, filename):
        availableDocs = self.availableDocumentsList(currentUser)
        if filename in availableDocs:
            return 0
        else:
            return 1

    def availableDocumentsList(self,currentUser):
        self.cur.execute("SELECT filename FROM hru "
                         "WHERE user = ? AND"
                         "(right = ? OR right = ?);",
                         [currentUser, "s", "o"])
        availableDocs= []
        for row in self.cur:
            availableDocs.append(row[0])
        return availableDocs

    def addUser(self, user, password):
        self.users.append(user)
        hash = MD5.new()
        hash.update(password.encode())
        # Записываем в таблицу с пользователями выданный логин-пароль
        self.cur.execute("INSERT INTO users (login, md5pass) "
                         "VALUES (?, ?);",
                         [user, sqlite3.Binary(hash.digest())])
        self.con.commit()
        # генерируем открытый и закрытый ключи
        key = RSA.generate(2048)
        f = open('storage/private/' + user + '.pem', 'wb')
        f.write(key.exportKey("PEM"))
        f.close()
        f = open('storage/public/' + user + '.pem', 'wb')
        f.write(key.publickey().exportKey("PEM"))
        f.close()
        # в матрице ХРУ для всех файлов записываем право n
        for doc in self.documents:
            self.cur.execute("INSERT INTO hru "
                             "(filename, user, right)"
                             "VALUES (?,?,?);",
                             [doc, user, "n"])
            self.con.commit()

    def deleteUser(self, user, deleteFiles=False):
        if user not in self.users:
            print("not existing user")
            return
        self.cur.execute("DELETE FROM hru WHERE user = ?",
                         [user])
        self.con.commit()
        self.cur.execute("DELETE FROM users WHERE login = ?",
                         [user])
        self.con.commit()
        if deleteFiles:
            filenamesToDelete = []
            self.cur.execute("SELECT filename FROM files "
                             "WHERE OWNER = ?",
                             [user])
            for row in self.cur:
                self.cur.execute("DELETE FROM files WHERE filename = ?",
                                 [row[0]])
                self.con.commit()
                # TODO добавить скрипт физического удаления файла

    # залогинясь под пользователем currentUser, изменить
    # право для пользователя user на right для файла filename
    def changeRight(self, currentUser, filename, right, user):
        if (user not in self.users) or (filename not in self.documents) or \
                (user not in self.users) or (right not in ["s", "n"]):
            return 1, "Not existing user or document or right"
        self.cur.execute("SELECT owner FROM files "
                         "WHERE filename = ?;",
                         [filename])
        owner = ""
        for row in self.cur:
            owner = row[0]
        if owner == currentUser:
            self.cur.execute("UPDATE hru SET "
                             "right = ? "
                             "WHERE user = ? AND filename = ?;",
                             [right, user, filename])
            self.con.commit()
            return 0, "You've changed right of "+ filename+" for "+ user
        else:
            return 1, "You're not owner of this file"


    def isUserOrFileExist(self,user,filename):
        if (user in self.users) and (filename in self.documents):
            return 0, "user or document exist"
        else:
            return 1, "not existing user or document"

    def isUserOwnerOfDocument(self,user, filename):
        owner = self.getOwner(filename)
        if owner == user:
            return 0, "You're owner of this document"
        else:
            return 1, "You're not owner of this document"


    def isDocumentSigned(self,user,filename):
        currentSign = self.getSign(filename)
        if currentSign == "-":
            return 0, "Document is not signed"
        else:
            return 1, "Document signed"

    def getSign(self,filename):
        self.cur.execute("SELECT sign FROM files "
                         "WHERE filename = ?;",
                         [filename])
        currentSign = ""
        for row in self.cur:
            currentSign = row[0]
        return currentSign

    def getOwner(self,filename):
        self.cur.execute("SELECT owner FROM files "
                         "WHERE filename = ?;",
                         [filename])
        owner = ""
        for row in self.cur:
            owner = row[0]
        return owner

    def signDocument(self, user, filename, sign):
        self.cur.execute("UPDATE files SET "
                         "sign = ? "
                         "WHERE owner = ? AND filename = ?;",
                         [sign, user, filename])
        self.con.commit()
        return 0, "You signed this document"
