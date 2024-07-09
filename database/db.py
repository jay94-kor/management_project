import sqlite3

def create_connection():
    return sqlite3.connect("budget.db")

def fetch_all_projects():
    conn = create_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM projects")
    projects = c.fetchall()
    conn.close()
    return [dict(zip(['id', 'name', 'description'], project)) for project in projects]

def insert_expense(expense):
    conn = create_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO expenses (project_id, category, item, amount, description, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (expense['project_id'], expense['category'], expense['item'], expense['amount'], expense['description'], expense['status']))
    conn.commit()
    conn.close()

def fetch_pending_expenses():
    conn = create_connection()
    c = conn.cursor()
    c.execute('''
        SELECT e.id, e.project_id, p.name as project_name, e.category, e.item, e.amount, e.description
        FROM expenses e
        JOIN projects p ON e.project_id = p.id
        WHERE e.status = 'pending'
    ''')
    expenses = [dict(zip([column[0] for column in c.description], row)) for row in c.fetchall()]
    conn.close()
    return expenses

def approve_expense_db(expense_id):
    conn = create_connection()
    c = conn.cursor()
    c.execute("UPDATE expenses SET status = 'approved' WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()

def reject_expense_db(expense_id):
    conn = create_connection()
    c = conn.cursor()
    c.execute("UPDATE expenses SET status = 'rejected' WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()


def get_approved_expenses(project_id, category, item):
    conn = create_connection()
    c = conn.cursor()
    c.execute('''
        SELECT SUM(amount) FROM expenses
        WHERE project_id = ? AND category = ? AND item = ? AND status = 'approved'
    ''', (project_id, category, item))
    result = c.fetchone()[0]
    conn.close()
    return result if result is not None else 0