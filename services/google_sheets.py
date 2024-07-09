
from googleapiclient.discovery import build
from google.oauth2 import service_account
import pandas as pd

# 구글 시트 API 설정
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'credentials/service_account.json'

credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=credentials)

SPREADSHEET_ID = 'your_google_sheets_id'

def read_sheet_data(sheet_range):
    """Google Sheets에서 데이터를 읽어옵니다."""
    try:
        result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=sheet_range).execute()
        return result.get('values', [])
    except Exception as e:
        print(f"Error reading Google Sheets data: {e}")
        return []

def write_sheet_data(sheet_range, values):
    """Google Sheets에 데이터를 씁니다."""
    try:
        body = {
            'values': values
        }
        result = service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID, range=sheet_range,
            valueInputOption="RAW", body=body).execute()
        return result
    except Exception as e:
        print(f"Error writing Google Sheets data: {e}")
        return None

def sync_data_with_db(fetch_db_data):
    """데이터베이스와 Google Sheets 간의 데이터를 동기화합니다."""
    # 데이터베이스에서 데이터 가져오기
    db_data = fetch_db_data()
    if not db_data:
        return
    
    # 데이터 형식을 Google Sheets에 맞게 변환
    values = [list(row) for row in db_data]
    
    # Google Sheets에 데이터 쓰기
    write_sheet_data('Sheet1!A1', values)

def fetch_db_data():
    """예시 데이터베이스에서 데이터를 가져오는 함수 (데이터베이스 모듈의 함수를 사용할 것)"""
    # 여기에 데이터베이스에서 데이터를 가져오는 코드를 작성하세요
    return [
        ["Category", "Subcategory", "Amount"],
        ["Project A", "Sub1", 1000],
        ["Project B", "Sub2", 1500]
    ]

if __name__ == "__main__":
    # Google Sheets와 데이터베이스 간의 데이터 동기화 테스트
    sync_data_with_db(fetch_db_data)
