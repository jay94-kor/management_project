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
    cursor.execute('SELECT id, project_code, name, client, pm, department, CAST(contract_amount AS INTEGER), CAST(expected_profit AS INTEGER), expected_profit_rate FROM Project')    
    projects = cursor.fetchall()
    conn.close()
    return projects

def add_project_item(project_id, category, item, description, quantity1, spec1, quantity2, spec2, unit_price, total_price, assigned_amount):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO ProjectItem (project_id, category, item, description, quantity1, spec1, quantity2, spec2, unit_price, total_price, assigned_amount)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (project_id, category, item, description, quantity1, spec1, quantity2, spec2, unit_price, total_price, assigned_amount))
    conn.commit()
    conn.close()

def get_project_items(project_code):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT pi.id, pi.project_id, pi.project_code, pi.category, pi.item, pi.description, 
           pi.quantity1, pi.spec1, pi.quantity2, pi.spec2, pi.unit_price, pi.total_price, 
           pi.assigned_amount, COALESCE(SUM(er.amount), 0) as total_expenditure
    FROM ProjectItem pi
    LEFT JOIN ExpenditureRequest er ON pi.project_id = er.project_id
    WHERE pi.project_code = ?
    GROUP BY pi.id
    ''', (project_code,))
    project_items = cursor.fetchall()
    conn.close()
    return project_items

def update_project_budget(project_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    # 프로젝트의 총 배정 금액 계산
    cursor.execute('''
    SELECT SUM(assigned_amount) FROM ProjectItem WHERE project_id = ?
    ''', (project_id,))
    total_assigned = cursor.fetchone()[0] or 0
    
    # 프로젝트의 총 지출액 계산
    cursor.execute('''
    SELECT SUM(amount) FROM ExpenditureRequest WHERE project_id = ? AND status = 'Approved'
    ''', (project_id,))
    total_expenditure = cursor.fetchone()[0] or 0
    
    # 프로젝트 정보 업데이트
    cursor.execute('''
    UPDATE Project
    SET contract_amount = ?,
        expected_profit = ? - total_expenditure,
        total_expenditure = ?,
        balance = ? - total_expenditure
    WHERE id = ?
    ''', (total_assigned, total_assigned, total_expenditure, total_assigned, project_id))
    
    conn.commit()
    conn.close()

def get_expenditure_requests():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT er.id, p.name, er.amount, er.expenditure_type, er.description, er.planned_date, er.file_name, er.file_contents
    FROM ExpenditureRequest er
    JOIN Project p ON er.project_id = p.id
    WHERE er.status = 'Pending'
    ''')
    requests = cursor.fetchall()
    conn.close()
    return requests

def add_expenditure_request(project_item_id, amount, expenditure_type, description, date, file_name, file_contents):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT project_id, project_code FROM ProjectItem WHERE id = ?', (project_item_id,))
    project_id, project_code = cursor.fetchone()
    
    cursor.execute('''
    INSERT INTO ExpenditureRequest (project_id, project_code, project_item_id, amount, expenditure_type, description, planned_date, file_name, file_contents, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pending')
    ''', (project_id, project_code, project_item_id, amount, expenditure_type, description, date, file_name, file_contents))
    
    cursor.execute('''
    UPDATE ProjectItem
    SET assigned_amount = assigned_amount - ?
    WHERE id = ?
    ''', (amount, project_item_id))
    
    conn.commit()
    conn.close()

def get_project_by_id(project_code):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Project WHERE project_code = ?', (project_code,))
    project = cursor.fetchone()
    conn.close()
    return project

def get_project_expenditures(project_code):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM ExpenditureRequest WHERE project_code = ?', (project_code,))
    expenditures = cursor.fetchall()
    conn.close()
    return expenditures

def cancel_expenditure_request(request_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT project_id, amount FROM ExpenditureRequest
    WHERE id = ?
    ''', (request_id,))
    request = cursor.fetchone()
    
    if request:
        cursor.execute('''
        DELETE FROM ExpenditureRequest
        WHERE id = ?
        ''', (request_id,))
    
    conn.commit()
    conn.close()