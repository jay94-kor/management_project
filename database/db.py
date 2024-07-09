import sqlite3
from sqlite3 import Error

def create_connection():
    """데이터베이스에 연결을 생성합니다."""
    conn = None
    try:
        conn = sqlite3.connect(':memory:')  # 메모리 내에 데이터베이스 생성
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return conn

def create_table(conn):
    """budget 테이블을 생성합니다."""
    try:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS budget (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                subcategory TEXT NOT NULL,
                amount REAL NOT NULL
            )
        ''')
        conn.commit()
        print("Table created successfully")
    except Error as e:
        print(f"The error '{e}' occurred")

def save_to_db(conn, data):
    """데이터를 budget 테이블에 저장합니다."""
    try:
        c = conn.cursor()
        c.executemany('''
            INSERT INTO budget (category, subcategory, amount)
            VALUES (?, ?, ?)
        ''', [(item['category'], item['subcategory'], item['amount']) for item in data])
        conn.commit()
        print("Data saved to DB successfully")
    except Error as e:
        print(f"The error '{e}' occurred")

def fetch_all_data(conn):
    """budget 테이블에서 모든 데이터를 조회합니다."""
    try:
        c = conn.cursor()
        c.execute('SELECT category, subcategory, amount FROM budget')
        return c.fetchall()
    except Error as e:
        print(f"The error '{e}' occurred")
        return []