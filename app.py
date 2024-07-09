import streamlit as st
import pandas as pd
from utils.openai_utils import classify_data
from database.db import create_connection, create_table, save_to_db, fetch_all_data
import plotly.express as px
from services.google_drive import monitor_and_convert
from services.google_sheets import read_sheet_data, sync_data_with_db

# Streamlit 시크릿에서 Google Drive 폴더 ID 가져오기
FOLDER_ID = st.secrets["google_drive"]["folder_id"]

# 파일 업로드를 Google Drive 폴더로 자동으로 처리
spreadsheet_id = monitor_and_convert(FOLDER_ID)

if spreadsheet_id:
    # Google Sheets 데이터 읽기
    sheet_data = read_sheet_data(spreadsheet_id, 'Sheet1!A1:C')
    df = pd.DataFrame(sheet_data[1:], columns=sheet_data[0])
    
    # 데이터 분류 및 저장
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

# Google Sheets와 데이터베이스 간의 데이터 동기화 버튼
if st.button('Sync with Google Sheets'):
    conn = create_connection()
    sync_data_with_db(spreadsheet_id, lambda: fetch_all_data(conn))