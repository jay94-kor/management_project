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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            프로젝트명 TEXT PRIMARY KEY
        )
    ''')
    conn.commit()
    conn.close()

def add_project(project_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT 프로젝트명 FROM projects WHERE 프로젝트명 = ?', (project_name,))
    if cursor.fetchone() is not None:
        conn.close()
        raise ValueError(f'프로젝트 "{project_name}"는 이미 존재합니다.')
    cursor.execute('INSERT INTO projects (프로젝트명) VALUES (?)', (project_name,))
    conn.commit()
    conn.close()

def delete_project(project_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM projects WHERE 프로젝트명 = ?', (project_name,))
    cursor.execute('DELETE FROM budget WHERE 프로젝트명 = ?', (project_name,))
    conn.commit()
    conn.close()

def update_project_name(old_name, new_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE projects SET 프로젝트명 = ? WHERE 프로젝트명 = ?', (new_name, old_name))
    cursor.execute('UPDATE budget SET 프로젝트명 = ? WHERE 프로젝트명 = ?', (new_name, old_name))
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

def get_all_budget_data():
    conn = get_db_connection()
    df = pd.read_sql_query('SELECT * FROM budget', conn)
    conn.close()
    return df

def get_project_names():
    conn = get_db_connection()
    df = pd.read_sql_query('SELECT DISTINCT 프로젝트명 FROM projects', conn)
    conn.close()
    return df['프로젝트명'].tolist()

def save_all_budget_data(df):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM budget')
    df.to_sql('budget', conn, if_exists='append', index=False)
    conn.commit()
    conn.close()