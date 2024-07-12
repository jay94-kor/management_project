import sqlite3

def initialize_db():
    conn = sqlite3.connect('budget_management.db')
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            client TEXT,
            created_by TEXT,
            created_at DATE,
            event_location TEXT,
            final_edit_date DATE,
            start_date DATE,
            end_date DATE
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS budget_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            category TEXT,
            sub_category TEXT,
            item TEXT,
            description TEXT,
            quantity INTEGER,
            unit TEXT,
            days INTEGER,
            times INTEGER,
            unit_price REAL,
            allocated_budget REAL,
            proposed_price REAL,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            project_id INTEGER,
            action TEXT,
            amount REAL,
            timestamp DATE,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    initialize_db()
