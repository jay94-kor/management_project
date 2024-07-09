def check_budget_warnings(project):
    warnings = []
    for category, item, allocated, remaining in zip(project['categories'], project['items'], project['allocated_amounts'], project['remaining_amounts']):
        if remaining < 0:
            warnings.append(f"{category} - {item}: 예산 초과 (배정: {allocated:,.0f}원, 잔액: {remaining:,.0f}원)")
        elif remaining / allocated < 0.1:
            warnings.append(f"{category} - {item}: 예산 부족 (배정: {allocated:,.0f}원, 잔액: {remaining:,.0f}원)")
    return warnings