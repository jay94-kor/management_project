import pandas as pd

def read_excel(file_path):
    df = pd.read_excel(file_path, sheet_name="예산 배정 및 정산서")
    return df

# 예시 사용법
if __name__ == "__main__":
    df = read_excel('path_to_excel_file.xlsx')
    print(df)
