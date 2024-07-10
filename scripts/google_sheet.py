import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
import json

def get_google_sheet(sheet_id):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    service_account_info = json.loads(st.secrets["gcp_service_account"]["service_account_info"])
    creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(sheet_id)
    
    # '예산 배정 및 정산서' 시트 찾기
    target_worksheet = None
    for worksheet in spreadsheet.worksheets():
        if "예산배정및정산서" in worksheet.title.replace(" ", ""):
            target_worksheet = worksheet
            break
    
    if target_worksheet is None:
        raise ValueError("Worksheet named '예산 배정 및 정산서' not found")
    
    return target_worksheet

def get_sheet_id(file_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    service_account_info = json.loads(st.secrets["gcp_service_account"]["service_account_info"])
    creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
    client = gspread.authorize(creds)
    
    try:
        spreadsheet = client.open(file_name)
        return spreadsheet.id
    except gspread.exceptions.SpreadsheetNotFound:
        raise FileNotFoundError(f"Spreadsheet named '{file_name}' not found in Google Sheets.")