from google.oauth2 import service_account
from googleapiclient.discovery import build
import streamlit as st

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def get_google_sheet(sheet_id):
    creds = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    
    # Get all sheets in the spreadsheet
    sheet_metadata = sheet.get(spreadsheetId=sheet_id).execute()
    sheets = sheet_metadata.get('sheets', '')
    
    # Find the sheet with '예산 배정 및 정산서' in its name
    target_sheet = None
    for s in sheets:
        if "예산배정및정산서" in s['properties']['title'].replace(" ", ""):
            target_sheet = s
            break
    
    if target_sheet is None:
        raise ValueError("Worksheet named '예산 배정 및 정산서' not found")
    
    range_name = f"{target_sheet['properties']['title']}!A1:O1000"
    result = sheet.values().get(spreadsheetId=sheet_id, range=range_name).execute()
    values = result.get('values', [])

    if not values:
        raise ValueError("No data found in the sheet")

    project_info = {
        "project_name": ' '.join(values[2][2:5]),
        "author": ' '.join(values[3][2:5]),
        "client": ' '.join(values[2][7:10]),
        "first_written_date": ' '.join(values[3][7:10]),
        "event_location": values[2][12],
        "last_written_date": values[3][12],
        "event_start_date": values[2][14],
        "event_end_date": values[3][14]
    }

    items = []
    for row in values[7:]:
        if len(row) >= 13 and row[0] and row[1] and row[2]:  # 대분류, 중분류, 소분류가 모두 있는 경우만
            item = {
                "category": row[0],
                "subcategory": row[1],
                "item": row[2],
                "description": row[3] if len(row) > 3 else "",
                "quantity": row[5] if len(row) > 5 else "",
                "spec": row[6] if len(row) > 6 else "",
                "days": row[7] if len(row) > 7 else "",
                "times": row[9] if len(row) > 9 else "",
                "unit_price": row[11] if len(row) > 11 else "",
                "assigned_budget": row[12] if len(row) > 12 else ""
            }
            items.append(item)

    # 제안가 (VAT포함) 찾기
    total_budget = None
    for row in reversed(values):
        if len(row) > 12 and "제안가 (VAT포함)" in row[0]:
            total_budget = row[12]
            break

    return {
        "project_info": project_info,
        "items": items,
        "total_budget": total_budget
    }