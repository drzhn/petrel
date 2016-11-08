# -*- coding: utf-8 -*-
"""
отладочный скрипт, записывающий в таблицу пользователей тестовые
логины и хэши паролей
"""
import sqlite3
from Crypto.Hash import MD5

con = sqlite3.connect('Petrel.db')
cur = con.cursor()

logPass = [["nikita", "12345"],
           ["nastya","1111111"],
           ["roman","456789"],
           ["masha","22222"]]

# hash.update(message.encode())
# print(hash.digest())

cur.execute('DROP TABLE IF EXISTS users ')
con.commit()

cur.execute('CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, login VARCHAR(100), md5pass BLOB)')
con.commit()
for lp in logPass:
    hash = MD5.new()
    hash.update(lp[1].encode())
    cur.execute("INSERT INTO users (login, md5pass) VALUES (?, ?);",
                [lp[0], sqlite3.Binary(hash.digest())])
    con.commit()

cur.execute('SELECT * FROM users')
for row in cur:
    print(row)
con.close()