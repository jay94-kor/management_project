import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
import json

def get_google_sheet(sheet_id):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    service_account_info = json.loads(st.secrets["gcp_service_account"]["service_account_info"])
    creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_id).sheet1
    return sheet

def get_sheet_id(sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    service_account_info = json.loads(st.secrets["gcp_service_account"]["service_account_info"])
    creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
    client = gspread.authorize(creds)
    sheet_list = client.openall()
    for sheet in sheet_list:
        if sheet.title == sheet_name:
            return sheet.id
    raise FileNotFoundError(f"Sheet named '{sheet_name}' not found in Google Sheets.")