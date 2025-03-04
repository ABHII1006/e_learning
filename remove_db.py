import os

if os.path.exists('subjects.db'):
    os.remove('subjects.db')
#
# import sqlite3
# conn = sqlite3.connect('users.db')
# cursor = conn.cursor()
# cursor.execute('INSERT INTO users (name,email,phone,password,courses) VALUES (?,?,?,?,?)',
#                        ('user2', 'user2@gmail.com', '9900886621' ,'12345u','python,java,cpp'))
# conn.commit()
# conn.close()