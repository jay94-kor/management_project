import sqlite3

def create_connection(db_file):
    conn = sqlite3.connect(db_file)
    return conn

def create_table(conn):
    c = conn.cursor()
    
    # 프로젝트 테이블 생성
    c.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT
        )
    ''')
    
    # 예산 테이블 생성
    c.execute('''
        CREATE TABLE IF NOT EXISTS budget (
            id INTEGER PRIMARY KEY,
            project_id INTEGER,
            date TEXT,
            category TEXT,
            subcategory TEXT,
            amount REAL,
            description TEXT,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
    ''')
    
    # 사용자 테이블 생성
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            has_approval_rights INTEGER DEFAULT 0
        )
    ''')
    
    conn.commit()

def insert_data(conn, data):
    c = conn.cursor()
    c.executemany('''
        INSERT INTO budget (project_id, date, category, subcategory, amount, description)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', data)
    conn.commit()

def fetch_all_data(conn):
    c = conn.cursor()
    c.execute('SELECT * FROM projects')
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