from database.db import fetch_all_projects, insert_expense, fetch_pending_expenses, approve_expense_db, reject_expense_db

def get_projects():
    return fetch_all_projects()

def add_expense(project_id, category, item, amount, description):
    new_expense = {
        'project_id': project_id,
        'category': category,
        'item': item,
        'amount': amount,
        'description': description,
        'status': 'pending'
    }
    insert_expense(new_expense)

def fetch_pending_expenses():
    return fetch_pending_expenses()

def approve_expense(expense_id):
    approve_expense_db(expense_id)

def reject_expense(expense_id):
    reject_expense_db(expense_id)