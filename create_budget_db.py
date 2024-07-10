import sqlite3
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_connection(db_file):
    """데이터베이스 연결을 생성합니다."""
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        logger.error(f"데이터베이스 연결 오류: {e}")
        return None

def create_tables(conn):
    """데이터베이스에 필요한 테이블을 생성합니다."""
    try:
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
        
        # 지출 테이블 생성
        c.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY,
                project_id INTEGER,
                category TEXT,
                item TEXT,
                amount REAL,
                description TEXT,
                status TEXT,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        ''')

        # budget_items 테이블 생성
        c.execute('''
            CREATE TABLE IF NOT EXISTS budget_items (
                id INTEGER PRIMARY KEY,
                project_name TEXT,
                category TEXT,
                item TEXT,
                description TEXT,
                quantity REAL,
                specification TEXT,
                input_rate REAL,
                unit_price REAL,
                amount REAL,
                allocated_amount REAL,
                budget_item TEXT,
                settled_amount REAL,
                expected_unit_price REAL,
                ordered_amount REAL,
                difference REAL,
                profit_rate REAL,
                company_name TEXT,
                partner_registered BOOLEAN,
                unregistered_reason TEXT,
                remarks TEXT,
                remaining_amount REAL
            )
        ''')
        
        conn.commit()
        logger.info("테이블이 성공적으로 생성되었습니다.")
    except sqlite3.Error as e:
        logger.error(f"테이블 생성 오류: {e}")

def main():
    database = "budget.db"
    conn = create_connection(database)
    
    if conn is not None:
        create_tables(conn)
        conn.close()
    else:
        logger.error("데이터베이스 연결을 생성할 수 없습니다.")

if __name__ == '__main__':
    main()