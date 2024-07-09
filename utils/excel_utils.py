import pandas as pd

def load_excel_data(uploaded_file, sheet_name=None):
    if sheet_name is None:
        xls = pd.ExcelFile(uploaded_file)
        sheet_name = xls.sheet_names[0]
    
    df = pd.read_excel(uploaded_file, sheet_name=sheet_name, header=4)
    df.ffill(axis=0, inplace=True)
    
    # 열 이름 설정 (필요한 경우 수정)
    df.columns = ['category', 'item', 'na1', 'description', 'quantity', 'specification', 'input_rate', 
                  'unit_price', 'amount', 'allocated_amount', 'budget_item', 'settled_amount', 
                  'expected_unit_price', 'ordered_amount', 'difference', 'profit_rate', 
                  'company_name', 'partner_registered', 'unregistered_reason', 'remarks']
    
    relevant_columns = ['category', 'item', 'description', 'quantity', 'specification', 'input_rate', 
                        'unit_price', 'amount', 'allocated_amount', 'budget_item', 'settled_amount', 
                        'expected_unit_price', 'ordered_amount', 'difference', 'profit_rate', 
                        'company_name', 'partner_registered', 'unregistered_reason', 'remarks']
    df = df[relevant_columns]
    
    return df