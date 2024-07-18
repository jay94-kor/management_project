# services/expenditure_service.py

from db.database import get_connection

def request_expenditure(project_item_id, requested_amount):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO ExpenditureRequest (project_item_id, requested_amount)
    VALUES (?, ?)
    ''', (project_item_id, requested_amount))
    conn.commit()
    conn.close()

def add_expenditure_request(project_item_id, amount, expenditure_type, description, date, file_name, file_contents):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT project_id, project_code FROM ProjectItem WHERE id = ?', (project_item_id,))
    project_id, project_code = cursor.fetchone()
    
    cursor.execute('''
    INSERT INTO ExpenditureRequest (project_id, project_code, project_item_id, amount, expenditure_type, reason, planned_date, file_name, file_contents)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (project_id, project_code, project_item_id, amount, expenditure_type, description, date, file_name, file_contents))
    
    cursor.execute('''
    UPDATE ProjectItem
    SET assigned_amount = assigned_amount - ?
    WHERE id = ?
    ''', (amount, project_item_id))
    
    conn.commit()
    conn.close()