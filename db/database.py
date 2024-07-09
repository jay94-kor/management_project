import sqlite3

def get_db_connection():
    conn = sqlite3.connect('budget_management.db')
    return conn

def insert_data_to_db(df):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        for index, row in df.iterrows():
            columns = ', '.join(row.index)
            placeholders = ', '.join(['?' for _ in row.index])
            query = f'''
                INSERT INTO budget_items (
                    {columns}
                ) VALUES ({placeholders})
            '''
            cursor.execute(query, tuple(row))
        
        conn.commit()
    except sqlite3.Error as e:
        print(f'데이터베이스 오류: {e}')
    finally:
        conn.close()
