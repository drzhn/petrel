from Crypto.Hash import MD5
from Crypto.Cipher import AES

def Login(login, password):
    hash = MD5.new()
    hash.update(password.encode())
    # print(hash.digest())
    obj = AES.new(hash.digest(), AES.MODE_CBC, 'BUREVESTNIK12345')
    ciphertext = obj.encrypt(login + "0" * (16 - len(login)))
    return ciphertext