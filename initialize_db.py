import sqlite3

def initialize_db():
    conn = sqlite3.connect('budget_management.db')
    cursor = conn.cursor()
    
    # 예산 항목 테이블 생성
    cursor.execute('''CREATE TABLE IF NOT EXISTS budget_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_name TEXT,
        category TEXT,
        item TEXT,
        description TEXT,
        allocated_amount REAL,
        used_amount REAL,
        remaining_amount REAL,
        company_name TEXT
    )''')

    # 회사 테이블 생성
    cursor.execute('''CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        contact_info TEXT
    )''')

    # 지출 내역 테이블 생성
    cursor.execute('''CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        budget_item_id INTEGER,
        amount REAL,
        date TEXT,
        requester_name TEXT,
        requester_email TEXT,
        requester_phone TEXT,
        FOREIGN KEY(budget_item_id) REFERENCES budget_items(id)
    )''')

    # 수정 요청 테이블 생성
    cursor.execute('''CREATE TABLE IF NOT EXISTS modification_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        budget_item_id INTEGER,
        requested_change TEXT,
        status TEXT,
        request_date TEXT,
        approval_date TEXT,
        approver_name TEXT,
        FOREIGN KEY(budget_item_id) REFERENCES budget_items(id)
    )''')

    # 사용자 테이블 생성 (로그인용)
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        email TEXT,
        phone TEXT
    )''')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    initialize_db()
    print("Database initialized successfully.")
