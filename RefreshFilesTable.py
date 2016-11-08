import sqlite3
from Crypto.Hash import MD5

con = sqlite3.connect('Petrel.db')
cur = con.cursor()

cur.execute('DROP TABLE IF EXISTS files ')
con.commit()

cur.execute('CREATE TABLE files ('
            'id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, '
            'filename VARCHAR(100), '
            'owner VARCHAR(100),'
            'sign VARCHAR(1000),'
            'date VARCHAR(100))')
con.commit()

cur.execute('DROP TABLE IF EXISTS hru ')
con.commit()

cur.execute('CREATE TABLE hru ('
            'filename VARCHAR(100), '
            'user VARCHAR(100),'
            'right VARCHAR(1))')
con.commit()