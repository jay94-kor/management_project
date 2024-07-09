import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import asyncio
import pandas as pd
from services.google_drive import get_project_list
from services.google_sheets import read_sheet_data, sync_data_with_db
from database.db import create_connection, create_table, fetch_all_data, insert_data, update_data, delete_data
from utils.openai_utils import classify_data
from utils.account_management import create_user_table, login, register, is_admin, grant_approval_rights
from utils.dashboard import create_dashboard

async def main():
    st.title("예산 관리 애플리케이션")

    # 사용자 테이블 생성
    create_user_table()

    # 데이터베이스 연결
    conn = create_connection("budget.db")
    create_table(conn)

    # 구글 드라이브 폴더 ID
    folder_id = st.secrets["google_drive"]["folder_id"]

    # 프로젝트 목록 표시
    st.subheader("프로젝트 목록")
    projects = await get_project_list(folder_id)
    project_names = [f"{project['code']}_{project['name']}" for project in projects]
    selected_project = st.selectbox("프로젝트를 선택하세요", project_names)

    if selected_project:
        st.write(f"선택된 프로젝트: {selected_project}")

        # 프로젝트 세부 정보 및 대시보드 표시
        project_data = [project for project in projects if f"{project['code']}_{project['name']}" == selected_project]
        create_dashboard(project_data)

        # 파일 업로드 및 데이터 분류
        uploaded_file = st.file_uploader("엑셀 파일을 업로드하세요", type="xlsx")
        if uploaded_file is not None:
            data = pd.read_excel(uploaded_file)
            classified_data = classify_data(data.to_json())
            st.write("분류된 데이터:", classified_data)
            if st.button("데이터베이스에 저장"):
                insert_data(conn, classified_data)
                st.success("데이터가 성공적으로 저장되었습니다.")

        # Google Sheets 동기화
        if st.button('Google Sheets와 동기화'):
            spreadsheet_id = st.session_state.get('spreadsheet_id')
            if spreadsheet_id:
                sync_data_with_db(spreadsheet_id, lambda: fetch_all_data(conn))
                st.success("데이터가 Google Sheets와 동기화되었습니다")
            else:
                st.error("스프레드시트 ID를 찾을 수 없습니다.")

        # 관리자 기능
        if 'user' in st.session_state and is_admin(st.session_state.user):
            st.subheader("관리자 기능")
            user_to_grant = st.text_input("승인 권한을 부여할 사용자명")
            if st.button("승인 권한 부여"):
                if grant_approval_rights(user_to_grant):
                    st.success(f"{user_to_grant}에게 승인 권한이 부여되었습니다.")
                else:
                    st.error("승인 권한 부여에 실패했습니다.")

        # 로그아웃
        if 'user' in st.session_state and st.button("로그아웃"):
            del st.session_state.user
            st.experimental_rerun()

if __name__ == "__main__":
    asyncio.run(main())