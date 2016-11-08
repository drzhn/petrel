import socket
import os
import json
from Crypto.Hash import MD5
from Client.Login import Login

from Client.ClientComands import executeCommands
from SecureConnection import *

clientSocket = socket.socket()

clientSocket.connect(("127.0.0.1", 10000))
print("LOGIN> ",end="")
login = input()
print("PASSWORD> ",end="")
password = input()
# login = "nikita"
# password = "12345"
hash = MD5.new()
hash.update(password.encode())
md5pass = hash.digest()

clientSocket.send(Login(login, password))
print(receive(clientSocket, md5pass).decode())

while True:
    print("#> ",end="")
    comand = input()
    if comand == "exit":
        send(clientSocket, "exit".encode(), md5pass)
        clientSocket.close()
        break
    executeCommands(comand,clientSocket,login, md5pass)

