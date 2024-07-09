import sqlite3
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_connection():
    """데이터베이스 연결을 생성합니다."""
    try:
        conn = sqlite3.connect("budget.db")
        return conn
    except sqlite3.Error as e:
        logger.error(f"데이터베이스 연결 오류: {e}")
        return None

def execute_query(conn, query, params=None):
    """SQL 쿼리를 실행합니다."""
    try:
        c = conn.cursor()
        if params:
            c.execute(query, params)
        else:
            c.execute(query)
        conn.commit()
        return c
    except sqlite3.Error as e:
        logger.error(f"쿼리 실행 오류: {e}")
        conn.rollback()
        return None

def fetch_all_projects():
    """모든 프로젝트를 조회합니다."""
    conn = create_connection()
    if conn is None:
        return []
    
    try:
        query = "SELECT * FROM projects"
        c = execute_query(conn, query)
        if c is None:
            return []
        
        projects = c.fetchall()
        return [dict(zip(['id', 'name', 'description'], project)) for project in projects]
    except Exception as e:
        logger.error(f"프로젝트 조회 오류: {e}")
        return []
    finally:
        conn.close()

def insert_expense(expense):
    """새로운 지출을 추가합니다."""
    conn = create_connection()
    if conn is None:
        return False
    
    try:
        query = '''
            INSERT INTO expenses (project_id, category, item, amount, description, status)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        params = (expense['project_id'], expense['category'], expense['item'], 
                  expense['amount'], expense['description'], expense['status'])
        
        c = execute_query(conn, query, params)
        return c is not None
    except Exception as e:
        logger.error(f"지출 추가 오류: {e}")
        return False
    finally:
        conn.close()

def fetch_pending_expenses():
    """승인 대기 중인 지출을 조회합니다."""
    conn = create_connection()
    if conn is None:
        return []
    
    try:
        query = '''
            SELECT e.id, e.project_id, p.name as project_name, e.category, e.item, e.amount, e.description
            FROM expenses e
            JOIN projects p ON e.project_id = p.id
            WHERE e.status = 'pending'
        '''
        c = execute_query(conn, query)
        if c is None:
            return []
        
        expenses = [dict(zip([column[0] for column in c.description], row)) for row in c.fetchall()]
        return expenses
    except Exception as e:
        logger.error(f"승인 대기 지출 조회 오류: {e}")
        return []
    finally:
        conn.close()

def approve_expense(expense_id):
    """지출을 승인합니다."""
    conn = create_connection()
    if conn is None:
        return False
    
    try:
        query = "UPDATE expenses SET status = 'approved' WHERE id = ?"
        c = execute_query(conn, query, (expense_id,))
        return c is not None
    except Exception as e:
        logger.error(f"지출 승인 오류: {e}")
        return False
    finally:
        conn.close()

def reject_expense(expense_id):
    """지출을 거부합니다."""
    conn = create_connection()
    if conn is None:
        return False
    
    try:
        query = "UPDATE expenses SET status = 'rejected' WHERE id = ?"
        c = execute_query(conn, query, (expense_id,))
        return c is not None
    except Exception as e:
        logger.error(f"지출 거부 오류: {e}")
        return False
    finally:
        conn.close()

def get_approved_expenses(project_id, category, item):
    """승인된 지출의 총액을 조회합니다."""
    conn = create_connection()
    if conn is None:
        return 0
    
    try:
        query = '''
            SELECT SUM(amount) FROM expenses
            WHERE project_id = ? AND category = ? AND item = ? AND status = 'approved'
        '''
        c = execute_query(conn, query, (project_id, category, item))
        if c is None:
            return 0
        
        result = c.fetchone()[0]
        return result if result is not None else 0
    except Exception as e:
        logger.error(f"승인된 지출 조회 오류: {e}")
        return 0
    finally:
        conn.close()