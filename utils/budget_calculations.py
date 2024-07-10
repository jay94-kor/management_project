def calculate_remaining_amount(allocated_amount, used_amount):
    return allocated_amount - used_amount

def handle_over_budget(project_name, over_amount):
    print(f"프로젝트 {project_name}에서 {over_amount}원 초과 지출되었습니다.")