import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import asyncio
import pandas as pd
from services.google_drive import get_project_list
from services.google_sheets import read_sheet_data, sync_data_with_db
from database.db import create_connection, create_table, fetch_all_data, insert_data, update_data, delete_data, fetch_pending_expenses, approve_expense, reject_expense
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
    project_names = [f"{project['name']}" for project in projects]

    cols = st.columns(3)
    for i, project in enumerate(projects):
        with cols[i % 3]:
            st.write(f"### {project['name']}")
            st.write(f"프로젝트 이름: {project['name']}")
            if st.button(f"지출 추가하기 - {project['name']}", key=f"add_expense_{project['name']}_{i}"):
                st.session_state.selected_project = project
                st.experimental_rerun()

    if 'selected_project' in st.session_state:
        selected_project = st.session_state.selected_project
        st.write(f"선택된 프로젝트: {selected_project['code']}_{selected_project['name']}")

        # 지출 추가 폼
        st.subheader("지출 추가")
        date = st.date_input("날짜")
        category = st.text_input("카테고리")
        subcategory = st.text_input("서브카테고리")
        amount = st.number_input("금액", min_value=0.0)
        description = st.text_area("설명")

        if st.button("지출 추가"):
            new_expense = (selected_project['id'], date, category, subcategory, amount, description)
            insert_data(conn, [new_expense])
            st.success("지출이 성공적으로 추가되었습니다.")
            del st.session_state.selected_project
            st.experimental_rerun()

        # 승인 프로세스
        if 'user' in st.session_state and is_admin(st.session_state.user):
            st.subheader("승인 대기 중인 지출")
            pending_expenses = fetch_pending_expenses(conn, selected_project['id'])
            for expense in pending_expenses:
                st.write(expense)
                if st.button(f"승인 - {expense[0]}", key=f"approve_{expense[0]}"):
                    approve_expense(conn, expense[0])
                    st.success("지출이 승인되었습니다.")
                if st.button(f"반려 - {expense[0]}", key=f"reject_{expense[0]}"):
                    reject_expense(conn, expense[0])
                    st.error("지출이 반려되었습니다.")

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