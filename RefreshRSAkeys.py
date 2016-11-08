from Crypto.Random import random
from Crypto.PublicKey import DSA
from Crypto.Hash import SHA256
message = "Hello"
# key = DSA.generate(1024)
h = SHA256.new(message.encode()).digest()
# k = random.StrongRandom().randint(1,key.q-1)
#
# sig = key.sign(h,k)
#
#
# if key.verify(h,sig):
#     print("OK")
# else:
#     print("Incorrect signature")

# import sqlite3
from Crypto.PublicKey import RSA
#
# con = sqlite3.connect('Petrel.db')
# cur = con.cursor()
# cur.execute('SELECT * FROM users')
# for row in cur:
#     login = row[1]
#     key = RSA.generate(2048)
#     f = open('storage/private/'+login+'.pem','wb')
#     f.write(key.exportKey("PEM"))
#     f.close()
#     f = open('storage/public/'+login+'.pem','wb')
#     f.write(key.publickey().exportKey("PEM"))
#     f.close()

f = open('private.pem','r')
key = RSA.importKey(f.read())
k = random.StrongRandom().randint(1,key.q-1)
sig = key.sign(h,k)

signature = str(sig)
print(signature)
print(len(signature))

signature_tuple = eval(signature)
f = open('public.pem','r')
public_key = RSA.importKey(f.read())
if public_key.verify(h,signature_tuple):
    print("OK")
else:
    print("Incorrect signature")

