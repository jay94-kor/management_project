from googleapiclient.discovery import build
from google.oauth2 import service_account
import streamlit as st
import json
import os

# Google Sheets API 설정
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_INFO = json.loads(os.environ.get('GCP_SERVICE_ACCOUNT'))

credentials = service_account.Credentials.from_service_account_info(
    SERVICE_ACCOUNT_INFO, scopes=SCOPES)
service = build('sheets', 'v4', credentials=credentials)

def read_sheet_data(spreadsheet_id, sheet_range):
    """Google Sheets에서 데이터를 읽어옵니다."""
    try:
        result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=sheet_range).execute()
        return result.get('values', [])
    except Exception as e:
        print(f"Error reading Google Sheets data: {e}")
        return []

def write_sheet_data(spreadsheet_id, sheet_range, values):
    """Google Sheets에 데이터를 씁니다."""
    try:
        body = {
            'values': values
        }
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=sheet_range,
            valueInputOption="RAW", body=body).execute()
        return result
    except Exception as e:
        print(f"Error writing Google Sheets data: {e}")
        return None

def sync_data_with_db(spreadsheet_id, fetch_db_data):
    """데이터베이스와 Google Sheets 간의 데이터를 동기화합니다."""
    # 데이터베이스에서 데이터 가져오기
    db_data = fetch_db_data()
    if not db_data:
        return
    
    # 데이터 형식을 Google Sheets에 맞게 변환
    values = [list(row) for row in db_data]
    
    # Google Sheets에 데이터 쓰기
    write_sheet_data(spreadsheet_id, 'Sheet1!A1', values)
