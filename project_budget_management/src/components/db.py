import sqlite3
from contextlib import contextmanager

@contextmanager
def db_connection():
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()

def get_db_connection():
    conn = sqlite3.connect('budget_management.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_projects():
    conn = get_db_connection()
    projects = conn.execute('SELECT * FROM projects').fetchall()
    conn.close()
    return projects

def get_budget_items(project_id):
    conn = get_db_connection()
    budget_items = conn.execute('SELECT * FROM budget_items WHERE project_id = ?', (project_id,)).fetchall()
    conn.close()
    return budget_items

def get_users():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return users

def get_logs():
    conn = get_db_connection()
    logs = conn.execute('SELECT * FROM logs').fetchall()
    conn.close()
    return logs