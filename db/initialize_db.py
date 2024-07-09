import sqlite3

def initialize_db():
    conn = sqlite3.connect('budget_management.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS budget_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            partner_registered TEXT,
            unregistered_reason TEXT,
            remarks TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            contact_info TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            budget_item_id INTEGER,
            amount REAL,
            date TEXT,
            requester_name TEXT,
            requester_email TEXT,
            requester_phone TEXT,
            FOREIGN KEY(budget_item_id) REFERENCES budget_items(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    
    cursor.execute('SELECT * FROM users WHERE username = ?', ('admin',))
    if cursor.fetchone() is None:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', ('admin', 'admin'))

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS modification_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            budget_item_id INTEGER,
            requested_change TEXT,
            requester_name TEXT,
            status TEXT DEFAULT 'Pending',
            approval_date TEXT,
            approver_name TEXT,
            FOREIGN KEY(budget_item_id) REFERENCES budget_items(id)
        )
    ''')

    conn.commit()
    conn.close()

# Initialize the database
initialize_db()
