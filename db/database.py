import sqlite3

def get_db_connection():
    conn = sqlite3.connect('budget_management.db')
    return conn

def insert_data_to_db(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        for item in data:
            columns = ', '.join(item.keys())
            placeholders = ', '.join(['?' for _ in item])
            values = tuple(item.values())
            query = f"INSERT INTO budget_items ({columns}) VALUES ({placeholders})"
            cursor.execute(query, values)
        
        conn.commit()
    except sqlite3.Error as e:
        print(f'데이터베이스 오류: {e}')
    finally:
        conn.close()