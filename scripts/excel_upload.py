import pandas as pd

def read_excel(file_path):
    df = pd.read_excel(file_path, sheet_name="예산 배정 및 정산서", header=None)
    
    # 프로젝트 정보 추출
    project_info = {
        "project_name": df.iloc[2, 2:5].values,
        "author": df.iloc[3, 2:5].values,
        "client": df.iloc[2, 7:10].values,
        "first_written_date": df.iloc[3, 7:10].values,
        "event_location": df.iloc[2, 12],
        "last_written_date": df.iloc[3, 12],
        "event_start_date": df.iloc[2, 14],
        "event_end_date": df.iloc[3, 14]
    }
    
    # 항목 데이터 추출
    items = df.iloc[7:, [0, 1, 2, 3, 5, 6, 7, 9, 11, 12, 13]]
    items.columns = ["category", "subcategory", "item", "description", "quantity", "spec", "days", "times", "unit_price", "assigned_budget", "proposed_price"]
    
    return project_info, items

# 예시 사용법
if __name__ == "__main__":
    file_path = 'path_to_excel_file.xlsx'
    project_info, items = read_excel(file_path)
    print("Project Info:", project_info)
    print("Items Data:", items)