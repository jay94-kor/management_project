import streamlit as st
import pandas as pd
from utils.openai_utils import classify_data
from database.db import create_connection, create_table, save_to_db, fetch_all_data
import plotly.express as px
from googleapiclient.discovery import build
from google.oauth2 import service_account

# 구글 시트 API 설정
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'credentials/service_account.json'
SPREADSHEET_ID = 'your-spreadsheet-id'

credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=credentials)

# 파일 업로드
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("Uploaded Data:")
    st.write(df)
    data = df.to_dict(orient='records')
    classified_data = classify_data(data)
    conn = create_connection()
    create_table(conn)
    save_to_db(conn, classified_data)
    st.write("Data classified and saved to the database")

    # 데이터 시각화
    db_data = fetch_all_data(conn)
    df = pd.DataFrame(db_data, columns=['category', 'subcategory', 'amount'])
    
    # 프로젝트별 총 예산
    fig1 = px.bar(df, x='category', y='amount', title='Total Budget per Project')
    st.plotly_chart(fig1)

    # 잔여 예산 및 평균 잔여 예산
    remaining_budget = df.groupby('category')['amount'].sum().reset_index()
    average_remaining_budget = remaining_budget['amount'].mean()

    fig2 = px.bar(remaining_budget, x='category', y='amount', title='Remaining Budget per Project')
    st.plotly_chart(fig2)

    st.write(f"Average Remaining Budget: {average_remaining_budget}")

# 시트 데이터 읽기
def read_sheet_data(sheet_range):
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=sheet_range).execute()
    return result.get('values', [])

# 시트 데이터 쓰기
def write_sheet_data(sheet_range, values):
    body = {
        'values': values
    }
    result = service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID, range=sheet_range,
        valueInputOption="RAW", body=body).execute()
    return result

# 데이터 동기화
def sync_data():
    conn = create_connection()
    db_data = fetch_all_data(conn)
    write_sheet_data('Sheet1!A1', db_data)
    st.write("Data synchronized with Google Sheets")

if st.button('Sync with Google Sheets'):
    sync_data()
