# services/project_service.py

from db.database import get_connection

def add_project(name, client, pm, department, contract_amount, expected_profit):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO Project (name, client, pm, department, contract_amount, expected_profit)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, client, pm, department, contract_amount, expected_profit))
    conn.commit()
    conn.close()

def get_projects():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, client, pm, department, contract_amount, expected_profit FROM Project')
    projects = cursor.fetchall()
    conn.close()
    return projects

def add_project_item(project_id, category, item, description, quantity, unit, period, period_unit, unit_price, total_price, assigned_amount):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO ProjectItem (project_id, category, item, description, quantity, unit, period, period_unit, unit_price, total_price, assigned_amount)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (project_id, category, item, description, quantity, unit, period, period_unit, unit_price, total_price, assigned_amount))
    conn.commit()
    conn.close()

def get_project_items(project_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM ProjectItem WHERE project_id = ?', (project_id,))
    project_items = cursor.fetchall()
    conn.close()
    return project_items