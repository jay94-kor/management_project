import pandas as pd

def read_excel(file_path):
    # 엑셀 파일의 모든 시트 이름 가져오기
    xls = pd.ExcelFile(file_path)
    sheet_name = None
    
    # 시트 이름 확인
    for name in xls.sheet_names:
        if "예산배정및정산서" in name.replace(" ", ""):
            sheet_name = name
            break
    
    if sheet_name is None:
        raise ValueError("Worksheet named '예산 배정 및 정산서' not found")
    
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
    
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
    
    # 병합된 셀 처리
    items = items.ffill()
    
    # "소계" 키워드가 포함된 행 제외
    items = items[~items["item"].str.contains("소계", na=False)]
    
    # unit_price가 0인 행 제외
    items = items[items["unit_price"] != 0]
    
    # subcategory에서 "VAT", "기업이윤", "일반관리비" 관련 행 제외
    items = items[~items["subcategory"].str.contains("VAT|기업이윤|일반관리비", na=False)]
    
    return project_info, items

# 예시 사용법
if __name__ == "__main__":
    file_path = 'path_to_excel_file.xlsx'
    project_info, items = read_excel(file_path)
    print("Project Info:", project_info)
    print("Items Data:", items)