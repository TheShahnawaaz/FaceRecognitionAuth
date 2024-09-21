# database.py
import sqlite3
import pickle

def initialize_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            encoding BLOB NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_user(name, encoding):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    encoded_data = pickle.dumps(encoding)
    c.execute('INSERT INTO users (name, encoding) VALUES (?, ?)', (name, encoded_data))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT name, encoding FROM users')
    users = c.fetchall()
    conn.close()
    processed_users = []
    for name, encoding in users:
        processed_users.append((name, pickle.loads(encoding)))
    return processed_users
