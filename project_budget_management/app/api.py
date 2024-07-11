import sqlite3
from datetime import datetime
from app.db import create_connection
from app.utils import log_action

def transfer_budget_item(conn, from_item_id, to_item_id, amount):
    cur = conn.cursor()

    # Get the current budgets
    cur.execute("SELECT allocated_budget, actual_cost FROM budget_items WHERE id=?", (from_item_id,))
    from_item = cur.fetchone()
    cur.execute("SELECT allocated_budget, actual_cost FROM budget_items WHERE id=?", (to_item_id,))
    to_item = cur.fetchone()

    if from_item and to_item:
        from_allocated_budget, from_actual_cost = from_item
        to_allocated_budget, to_actual_cost = to_item

        # Check if the transfer is possible
        if from_allocated_budget - from_actual_cost >= amount:
            new_from_allocated_budget = from_allocated_budget - amount
            new_to_allocated_budget = to_allocated_budget + amount

            # Update the budgets
            cur.execute("UPDATE budget_items SET allocated_budget=? WHERE id=?", (new_from_allocated_budget, from_item_id))
            cur.execute("UPDATE budget_items SET allocated_budget=? WHERE id=?", (new_to_allocated_budget, to_item_id))

            # Log the transfer
            log_action(conn, None, f"Transferred {amount} from item {from_item_id} to item {to_item_id}")
            conn.commit()
            return True
    return False

def transfer_budget_project(conn, from_project_id, to_project_id, amount):
    cur = conn.cursor()

    # Get the current project budgets
    cur.execute("SELECT SUM(allocated_budget - actual_cost) FROM budget_items WHERE project_id=?", (from_project_id,))
    from_project_budget = cur.fetchone()[0]
    cur.execute("SELECT SUM(allocated_budget - actual_cost) FROM budget_items WHERE project_id=?", (to_project_id,))
    to_project_budget = cur.fetchone()[0]

    if from_project_budget and to_project_budget:
        # Check if the transfer is possible
        if from_project_budget >= amount:
            cur.execute("""
                UPDATE budget_items
                SET allocated_budget = allocated_budget - ?
                WHERE project_id = ? AND (allocated_budget - actual_cost) >= ?
                LIMIT 1
            """, (amount, from_project_id, amount))
            cur.execute("""
                UPDATE budget_items
                SET allocated_budget = allocated_budget + ?
                WHERE project_id = ?
                LIMIT 1
            """, (amount, to_project_id))

            # Log the transfer
            log_action(conn, None, f"Transferred {amount} from project {from_project_id} to project {to_project_id}")
            conn.commit()
            return True
    return False

def request_budget_change(conn, project_id, item_id, new_amount):
    sql = ''' INSERT INTO logs(project_id, action, timestamp, details)
              VALUES(?,?,?,?) '''
    cur = conn.cursor()
    details = f"Request to change budget item {item_id} to {new_amount}"
    cur.execute(sql, (project_id, "request", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), details))
    conn.commit()

def approve_budget_change(conn, log_id):
    cur = conn.cursor()
    cur.execute("SELECT details FROM logs WHERE id=?", (log_id,))
    row = cur.fetchone()
    if row:
        details = row[0]
        parts = details.split()
        item_id = parts[4]
        new_amount = float(parts[-1])

        cur.execute("UPDATE budget_items SET allocated_budget=? WHERE id=?", (new_amount, item_id))
        cur.execute("UPDATE logs SET action='approved' WHERE id=?", (log_id,))
        conn.commit()
        log_action(conn, None, "approve", f"Approved budget change for item {item_id} to {new_amount}")

def reject_budget_change(conn, log_id, reason):
    cur = conn.cursor()
    cur.execute("UPDATE logs SET action='rejected', details=details || ' Rejected: ' || ? WHERE id=?", (reason, log_id))
    conn.commit()
