import sqlite3
import pandas as pd

def get_db_connection():
    conn = sqlite3.connect('database.db')
    return conn

def initialize_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS budget (
            id INTEGER PRIMARY KEY,
            프로젝트명 TEXT,
            구분 TEXT,
            예산과목 TEXT,
            항목 TEXT,
            내용 TEXT,
            수량 INTEGER,
            규격 TEXT,
            일수 INTEGER,
            일수_규격 TEXT,
            회 INTEGER,
            회_규격 TEXT,
            단가 INTEGER,
            배정_금액 INTEGER,
            수주금액 INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def add_budget_entry(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO budget (프로젝트명, 구분, 예산과목, 항목, 내용, 수량, 규격, 일수, 일수_규격, 회, 회_규격, 단가, 배정_금액, 수주금액)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', data)
    conn.commit()
    conn.close()

def get_budget_data(project_name):
    conn = get_db_connection()
    df = pd.read_sql_query('SELECT * FROM budget WHERE 프로젝트명 = ?', conn, params=(project_name,))
    conn.close()
    return df

def get_project_names():
    conn = get_db_connection()
    df = pd.read_sql_query('SELECT DISTINCT 프로젝트명 FROM budget', conn)
    conn.close()
    return df['프로젝트명'].tolist()
