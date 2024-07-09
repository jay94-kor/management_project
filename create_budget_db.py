import sqlite3

def create_connection(db_file):
    """ 데이터베이스 연결을 생성합니다. """
    conn = sqlite3.connect(db_file)
    return conn

def create_tables(conn):
    """ 데이터베이스에 필요한 테이블을 생성합니다. """
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

def main():
    database = "budget.db"
    
    # 데이터베이스 연결 생성
    conn = create_connection(database)
    
    if conn is not None:
        # 테이블 생성
        create_tables(conn)
        print("데이터베이스와 테이블이 성공적으로 생성되었습니다.")
    else:
        print("데이터베이스 연결을 생성할 수 없습니다.")

if __name__ == '__main__':
    main()