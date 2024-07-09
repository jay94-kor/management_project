import streamlit as st
import pandas as pd
from utils.openai_utils import classify_data
from database.db import create_connection, create_table, save_to_db, fetch_all_data
import plotly.express as px
from services.google_drive import upload_file_to_drive, monitor_and_convert
from services.google_sheets import read_sheet_data, sync_data_with_db

# Streamlit 시크릿에서 Google Drive 폴더 ID 가져오기
FOLDER_ID = st.secrets["google_drive"]["folder_id"]

# 데이터베이스 연결 및 테이블 생성
conn = create_connection()
create_table(conn)

st.title("Management Project Dashboard")

# 파일 업로드 기능
uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx"])

if uploaded_file:
    # 파일을 Google Drive에 업로드
    file_name = uploaded_file.name
    with open(file_name, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    file_id = upload_file_to_drive(file_name, FOLDER_ID)
    st.write(f"File uploaded to Google Drive with ID: {file_id}")

    # Google Drive 폴더를 모니터링하고 새로운 엑셀 파일을 Google Sheets로 변환
    spreadsheet_id = monitor_and_convert(FOLDER_ID)

    if spreadsheet_id:
        # Google Sheets 데이터 읽기
        sheet_data = read_sheet_data(spreadsheet_id, 'Sheet1!A1:C')
        
        # 디버깅: sheet_data 출력
        st.write("Sheet Data:", sheet_data)
        
        if len(sheet_data) > 1:
            df = pd.DataFrame(sheet_data[1:], columns=sheet_data[0])
            
            # 데이터 분류 및 저장
            data = df.to_dict(orient='records')
            classified_data = classify_data(data)
            save_to_db(conn, classified_data)
            st.write("Data classified and saved to the database")

            # 데이터 시각화
            db_data = fetch_all_data(conn)
            df = pd.DataFrame(db_data, columns=['category', 'subcategory', 'amount'])
            
            # 프로젝트별 총 예산
            st.subheader("Total Budget per Project")
            fig1 = px.bar(df, x='category', y='amount', title='Total Budget per Project')
            st.plotly_chart(fig1)

            # 잔여 예산 및 평균 잔여 예산
            st.subheader("Remaining Budget per Project")
            remaining_budget = df.groupby('category')['amount'].sum().reset_index()
            average_remaining_budget = remaining_budget['amount'].mean()

            fig2 = px.bar(remaining_budget, x='category', y='amount', title='Remaining Budget per Project')
            st.plotly_chart(fig2)

            st.write(f"Average Remaining Budget: {average_remaining_budget}")
        else:
            st.error("The uploaded Google Sheet is empty or does not have enough data.")
    else:
        st.error("Failed to convert the uploaded file to Google Sheets.")

# Google Sheets와 데이터베이스 간의 데이터 동기화 버튼
if st.button('Sync with Google Sheets'):
    sync_data_with_db(spreadsheet_id, lambda: fetch_all_data(conn))
    st.success("Data synchronized with Google Sheets")

# 데이터베이스 상태 확인
st.subheader("Database Status")
db_data = fetch_all_data(conn)
if db_data:
    df = pd.DataFrame(db_data, columns=['category', 'subcategory', 'amount'])
    st.dataframe(df)
else:
    st.write("No data found in the database.")