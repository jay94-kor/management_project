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

def approve_expenditure(request_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE ExpenditureRequest
    SET status = 'Approved'
    WHERE id = ?
    ''', (request_id,))
    
    cursor.execute('''
    SELECT project_item_id, requested_amount FROM ExpenditureRequest
    WHERE id = ?
    ''', (request_id,))
    request = cursor.fetchone()
    
    cursor.execute('''
    UPDATE ProjectItem
    SET total_amount = total_amount + ?
    WHERE id = ?
    ''', (request[1], request[0]))
    
    cursor.execute('''
    UPDATE Project
    SET total_expenditure = total_expenditure + ?
    WHERE id = (SELECT project_id FROM ProjectItem WHERE id = ?)
    ''', (request[1], request[0]))
    
    conn.commit()
    conn.close()
