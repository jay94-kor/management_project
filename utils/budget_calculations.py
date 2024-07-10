def calculate_remaining_amount(allocated_amount, used_amount):
    """잔액 계산 함수"""
    return allocated_amount - used_amount

def handle_over_budget(project_name, over_amount):
    """초과 지출 처리 함수"""
    print(f"프로젝트 {project_name}에서 {over_amount}원 초과 지출되었습니다.")