import sqlite3

def create_connection():
    conn = sqlite3.connect('budget.db')
    return conn

def create_table(conn):
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS budget (
        id INTEGER PRIMARY KEY,
        category TEXT,
        subcategory TEXT,
        amount REAL
    )
    ''')
    conn.commit()

def save_to_db(conn, data):
    c = conn.cursor()
    for row in data:
        c.execute('INSERT INTO budget (category, subcategory, amount) VALUES (?, ?, ?)', 
                  (row['category'], row['subcategory'], row['amount']))
    conn.commit()

def fetch_all_data(conn):
    c = conn.cursor()
    c.execute('SELECT category, subcategory, amount FROM budget')
    return c.fetchall()
