import sqlite3

def create_connection(db_file):
    conn = sqlite3.connect(db_file)
    return conn

def create_table(conn):
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS budget (
            id INTEGER PRIMARY KEY,
            date TEXT,
            category TEXT,
            subcategory TEXT,
            amount REAL,
            description TEXT
        )
    ''')
    conn.commit()

def insert_data(conn, data):
    c = conn.cursor()
    c.executemany('''
        INSERT INTO budget (date, category, subcategory, amount, description)
        VALUES (?, ?, ?, ?, ?)
    ''', data)
    conn.commit()

def fetch_all_data(conn):
    c = conn.cursor()
    c.execute('SELECT * FROM budget')
    rows = c.fetchall()
    return rows

def update_data(conn, data):
    c = conn.cursor()
    c.execute('''
        UPDATE budget
        SET date = ?, category = ?, subcategory = ?, amount = ?, description = ?
        WHERE id = ?
    ''', data)
    conn.commit()

def delete_data(conn, id):
    c = conn.cursor()
    c.execute('DELETE FROM budget WHERE id = ?', (id,))
    conn.commit()