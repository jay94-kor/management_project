import sqlite3

def create_user_table():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            has_approval_rights INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def login(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    result = c.fetchone()
    conn.close()
    return result is not None

def register(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def is_admin(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT is_admin FROM users WHERE username=?", (username,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else False

def grant_approval_rights(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute("UPDATE users SET has_approval_rights=1 WHERE username=?", (username,))

        conn.commit()
        return True
    except sqlite3.Error:
        return False

    finally:
        conn.close()