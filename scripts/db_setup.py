import sqlite3

def create_db():
    conn = sqlite3.connect('/Users/jay/Documents/GitHub/test/project_budget_management/data/database.db')  # 절대 경로로 수정
    c = conn.cursor()
    
    # 프로젝트 테이블
    c.execute('''
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        client TEXT,
        created_by TEXT,
        created_at TEXT,
        location TEXT,
        start_date TEXT,
        end_date TEXT,
        budget_total REAL
    )
    ''')
    
    # 예산 항목 테이블
    c.execute('''
    CREATE TABLE IF NOT EXISTS budget_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        category TEXT,
        subcategory TEXT,
        item TEXT,
        description TEXT,
        quantity INTEGER,
        unit TEXT,
        unit_price REAL,
        assigned_budget REAL,
        proposed_budget REAL,
        created_at TEXT,
        FOREIGN KEY (project_id) REFERENCES projects (id)
    )
    ''')
    
    # 사용자 테이블
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password_hash TEXT,
        role TEXT,
        created_at TEXT
    )
    ''')
    
    # 로그 테이블
    c.execute('''
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        project_id INTEGER,
        action TEXT,
        details TEXT,
        timestamp TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (project_id) REFERENCES projects (id)
    )
    ''')
    
    # 요청 테이블
    c.execute('''
    CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        project_id INTEGER,
        type TEXT,
        status TEXT,
        details TEXT,
        created_at TEXT,
        updated_at TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (project_id) REFERENCES projects (id)
    )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_db()
    print("Database setup complete.")