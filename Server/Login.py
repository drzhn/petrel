# -*- coding: utf-8 -*-
"""
Функция логина. принимает хэндл коннекта
ждет приема 16 байт, зашифрованного при помощи AES
введенного логина пользователя, где ключ -- md5 от пароля.
сравнивает со всеми имеющимися в базе
 возвращает логин, если такой есть в базе и пароль подошел,
 возвращает строку, если логина-пароля в базе нет
"""
import sqlite3
from Crypto.Hash import MD5
from Crypto.Cipher import AES


def Login(connection):
    con = sqlite3.connect('Petrel.db')
    cur = con.cursor()
    data = connection.recv(16)
    cur.execute('SELECT * FROM users')
    for row in cur:
        login = row[1]
        md5pass = row[2]
        obj = AES.new(md5pass, AES.MODE_CBC, 'BUREVESTNIK12345')
        plaintext = obj.decrypt(data)
        if plaintext == (login + "0" * (16 - len(login))).encode():
            con.close()
            return login, md5pass
    con.close()
    return "", ""
