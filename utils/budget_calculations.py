from db.database import get_db_connection

def handle_over_budget(project_name, over_budget_amount):
    conn = get_db_connection()
    cursor = conn.cursor()

    # 다른 프로젝트에서 예산 이관 가능한지 확인
    cursor.execute("""
        SELECT project_name, SUM(remaining_amount) as available_budget
        FROM budget_items
        WHERE project_name != ? AND remaining_amount > 0
        GROUP BY project_name
        ORDER BY available_budget DESC
    """, (project_name,))
    
    available_projects = cursor.fetchall()

    for available_project, available_budget in available_projects:
        if available_budget >= over_budget_amount:
            # 예산 이관
            cursor.execute("""
                UPDATE budget_items
                SET remaining_amount = remaining_amount - ?
                WHERE project_name = ? AND remaining_amount > 0
                LIMIT 1
            """, (over_budget_amount, available_project))

            cursor.execute("""
                UPDATE budget_items
                SET remaining_amount = remaining_amount + ?
                WHERE project_name = ? AND remaining_amount < 0
                LIMIT 1
            """, (over_budget_amount, project_name))

            conn.commit()
            conn.close()
            return f"{available_project}에서 {project_name}으로 {over_budget_amount} 이관 완료"

        elif available_budget > 0:
            # 부분 이관
            cursor.execute("""
                UPDATE budget_items
                SET remaining_amount = 0
                WHERE project_name = ? AND remaining_amount > 0
            """, (available_project,))

            cursor.execute("""
                UPDATE budget_items
                SET remaining_amount = remaining_amount + ?
                WHERE project_name = ? AND remaining_amount < 0
                LIMIT 1
            """, (available_budget, project_name))

            over_budget_amount -= available_budget

    conn.close()
    return f"이관 가능한 예산 부족. {over_budget_amount} 초과 지출 남음"

def calculate_remaining_amount(allocated, used):
    return allocated - used