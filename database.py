import sqlite3

def connects():
    conn = sqlite3.connect('бот_для.db', check_same_thread=False)
    return conn

def cursors(conn):
    return conn.cursor()

def executes(cursor):
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (us_id INTEGER UNIQUE, us_name TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS docs (id INTEGER PRIMARY KEY AUTOINCREMENT, doc BLOB)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS news (id INTEGER PRIMARY KEY AUTOINCREMENT, text_new VARCHAR(100))''')
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS records (id INTEGER PRIMARY KEY AUTOINCREMENT, rs TEXT, dt TEXT, tm TEXT)''')

