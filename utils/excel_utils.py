import pandas as pd

def load_excel_data(file):
    """엑셀 파일을 로드하여 DataFrame으로 반환합니다."""
    try:
        df = pd.read_excel(file)
        return df
    except Exception as e:
        raise ValueError(f"엑셀 파일 로드 오류: {e}")