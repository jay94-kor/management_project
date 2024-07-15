import sqlite3

def create_database(db_path, schema_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 기존 테이블 삭제
    cursor.executescript('''
    DROP TABLE IF EXISTS ExpenditureRequest;
    DROP TABLE IF EXISTS ProjectItem;
    DROP TABLE IF EXISTS Project;
    ''')
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = f.read()
    
    cursor.executescript(schema)
    conn.commit()
    conn.close()
    print(f"Database created successfully at {db_path}")

if __name__ == "__main__":
    create_database('project_management.db', 'db/create_tables.sql')