from googleapiclient.discovery import build
from google.oauth2 import service_account
import streamlit as st
import json
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets API 설정
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_INFO = json.loads(st.secrets["gcp_service_account"]["service_account_info"])

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

def sync_data_with_sheets(spreadsheet_id, fetch_data_func):
    client = get_gspread_client()
    sheet = client.open_by_key(spreadsheet_id).sheet1
    data = fetch_data_func()
    sheet.clear()
    sheet.append_row(["Date", "Category", "Subcategory", "Amount", "Description"])
    for row in data:
        sheet.append_row(row)

def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(creds)
    return client

def read_sheet_data(spreadsheet_id, range_name):
    client = get_gspread_client()
    sheet = client.open_by_key(spreadsheet_id).worksheet(range_name)
    data = sheet.get_all_records()
    return data