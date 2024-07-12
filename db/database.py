# db/database.py

import sqlite3

def get_connection():
    conn = sqlite3.connect('project_management.db')
    return conn

def initialize_db():
    conn = get_connection()
    cursor = conn.cursor()
    with open('db/create_tables.sql', 'r') as f:
        cursor.executescript(f.read())
    conn.commit()
    conn.close()
