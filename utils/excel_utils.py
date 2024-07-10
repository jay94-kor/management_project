import pandas as pd

def load_excel_data(file):
    try:
        df = pd.read_excel(file)
        return df
    except Exception as e:
        raise ValueError(f"엑셀 파일 로드 오류: {e}")