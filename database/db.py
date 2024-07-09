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
            status TEXT DEFAULT 'pending',
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
    
    # 지출 테이블 생성
    c.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY,
            project_id TEXT,
            category TEXT,
            item TEXT,
            amount REAL,
            description TEXT,
            status TEXT
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

def fetch_pending_expenses(conn):
    c = conn.cursor()
    c.execute('''
        SELECT e.id, e.project_id, p.name as project_name, e.category, e.item, e.amount, e.description
        FROM expenses e
        JOIN projects p ON e.project_id = p.id
        WHERE e.status = 'pending'
    ''')
    expenses = [dict(zip([column[0] for column in c.description], row)) for row in c.fetchall()]
    return expenses

def approve_expense(conn, expense_id):
    c = conn.cursor()
    c.execute("UPDATE expenses SET status = 'approved' WHERE id = ?", (expense_id,))
    conn.commit()

def reject_expense(conn, expense_id):
    c = conn.cursor()
    c.execute("UPDATE expenses SET status = 'rejected' WHERE id = ?", (expense_id,))
    conn.commit()

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

def get_approved_expenses(project_id, category, item):
    conn = create_connection("budget.db")
    c = conn.cursor()
    c.execute('''
        SELECT SUM(amount) FROM expenses
        WHERE project_id = ? AND category = ? AND item = ? AND status = 'approved'
    ''', (project_id, category, item))
    result = c.fetchone()[0]
    conn.close()
    return result if result is not None else 0

def insert_expense(expense):
    conn = create_connection("budget.db")
    c = conn.cursor()
    c.execute('''
        INSERT INTO expenses (project_id, category, item, amount, description, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (expense['project_id'], expense['category'], expense['item'], expense['amount'], expense['description'], expense['status']))
    conn.commit()
    conn.close()