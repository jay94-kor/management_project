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

def create_user_table(conn):
    """사용자 테이블을 생성합니다."""
    try:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                is_admin INTEGER DEFAULT 0,
                has_approval_rights INTEGER DEFAULT 0
            )
        ''')
        conn.commit()
        logger.info("사용자 테이블이 성공적으로 생성되었습니다.")
    except sqlite3.Error as e:
        logger.error(f"사용자 테이블 생성 오류: {e}")

def main():
    database = "users.db"
    conn = create_connection(database)
    
    if conn is not None:
        create_user_table(conn)
        conn.close()
    else:
        logger.error("데이터베이스 연결을 생성할 수 없습니다.")

if __name__ == '__main__':
    main()