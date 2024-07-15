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
    SELECT project_id, amount FROM ExpenditureRequest
    WHERE id = ?
    ''', (request_id,))
    request = cursor.fetchone()
    
    cursor.execute('''
    UPDATE Project
    SET total_expenditure = total_expenditure + ?,
        expected_profit = expected_profit - ?
    WHERE id = ?
    ''', (request[1], request[1], request[0]))
    
    conn.commit()
    conn.close()

def reject_expenditure(request_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT project_id, amount FROM ExpenditureRequest
    WHERE id = ?
    ''', (request_id,))
    request = cursor.fetchone()
    
    if request:
        cursor.execute('''
        UPDATE ExpenditureRequest
        SET status = 'Rejected'
        WHERE id = ?
        ''', (request_id,))
        
        cursor.execute('''
        UPDATE Project
        SET expected_profit = expected_profit + ?
        WHERE id = ?
        ''', (request[1], request[0]))
    
    conn.commit()
    conn.close()