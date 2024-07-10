import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
import json

def get_google_sheet(sheet_id):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    service_account_info = json.loads(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_id).sheet1
    return sheet

# 예시 사용법
if __name__ == "__main__":
    sheet_id = "16MdrQJghAOhA4XTdDqLaHHf5IuSx5iGe"
    sheet = get_google_sheet(sheet_id)
    print(sheet.get_all_records())