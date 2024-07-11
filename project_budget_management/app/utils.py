import sqlite3
from datetime import datetime

def log_action(conn, project_id, action, details):
    sql = ''' INSERT INTO logs(project_id, action, timestamp, details)
              VALUES(?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, (project_id, action, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), details))
    conn.commit()

def get_logs(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM logs")
    rows = cur.fetchall()
    return rows
