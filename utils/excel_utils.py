import pandas as pd

def load_excel_data(uploaded_file, sheet_name=None):
    if sheet_name is None:
        xls = pd.ExcelFile(uploaded_file)
        sheet_name = xls.sheet_names[0]
    
    df = pd.read_excel(uploaded_file, sheet_name=sheet_name, header=4)
    df.ffill(axis=0, inplace=True)
    
    # 실제 열 수에 맞게 열 이름 설정
    columns = ['category', 'item', 'description', 'quantity', 'specification', 'input_rate', 
               'unit_price', 'amount', 'allocated_amount', 'budget_item', 'settled_amount', 
               'expected_unit_price', 'ordered_amount', 'difference', 'profit_rate', 
               'company_name', 'partner_registered', 'unregistered_reason', 'remarks']
    
    # 실제 데이터프레임의 열 수에 맞게 열 이름 조정
    df.columns = columns[:len(df.columns)]
    
    # 필요한 열만 선택
    df = df[columns]
    
    return df