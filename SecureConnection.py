# -*- coding: utf-8 -*-
"""
Функции, через которые будет осуществляться общение
между сервером и клиентом
Так как AES работает с блоками по 16 байт,
данные делятся на такие же блоки. Недостающие данные заменяются на \x00
в качестве ключа используется 16 байтный md5-хэш пароля
залогиненного пользователя
"""
from Crypto.Cipher import AES
import json
import os


def send(conn, data, key, size=1024):
    obj = AES.new(key, AES.MODE_CBC, 'BUREVESTNIK12345')
    data += b"\x00" * (size - len(data))
    ciphertext = obj.encrypt(data)
    conn.send(ciphertext)


def receive(conn, key, size=1024, crop=True):
    data = conn.recv(size)
    # print(data)
    obj2 = AES.new(key, AES.MODE_CBC, 'BUREVESTNIK12345')
    data = obj2.decrypt(data)
    # обрезаем сообщение, удаляя \x00 с краю
    if crop:
        index = len(data)
        for i in range(len(data)):
            if data[i] == 0:
                index = i
                break
        return data[:index]
    else:
        return data


def send_file(conn, key, path):
    file = open(path, "rb")
    size = os.path.getsize(path)
    fileName = path.split("/")[-1]
    fileInfo = {"filename": fileName, "size": size}
    j = json.dumps(fileInfo)
    # перед отправкой данных, посылаем информацию о файле
    send(conn, j.encode(), key)
    for i in range(size // 1024 + 1):
        data = file.read(1024)
        send(conn, data, key)
    # print("\nfile uploaded")
    file.close()


def receive_file(conn, key, dir=""):
    fileInfo = receive(conn, key)
    fileInfo = json.loads(fileInfo.decode())
    fileName = fileInfo["filename"]
    size = fileInfo["size"]
    buffer = b""
    for i in range(size // 1024 + 1):
        # print('<', end='')
        buffer += receive(conn, key, crop=False)
    # print("file received")
    file = open(dir + fileName, "wb")
    file.write(buffer[:size])
    file.close()
    return fileName
