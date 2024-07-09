import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import asyncio
import pandas as pd
from services.google_drive import monitor_and_convert
from services.google_sheets import read_sheet_data, sync_data_with_db
from database.db import create_connection, create_table, fetch_all_data, insert_data, update_data, delete_data
from utils.openai_utils import classify_data
from utils.account_management import create_user_table, login, register, is_admin, grant_approval_rights
from utils.dashboard import create_dashboard

async def main():
    st.title("예산 관리 애플리케이션")

    # 사용자 테이블 생성
    create_user_table()

    # 로그인 / 회원가입
    if 'user' not in st.session_state:
        choice = st.radio("로그인 또는 회원가입", ["로그인", "회원가입"])
        if choice == "로그인":
            username = st.text_input("사용자명")
            password = st.text_input("비밀번호", type="password")
            if st.button("로그인"):
                if login(username, password):
                    st.session_state.user = username
                    st.success("로그인 성공!")
                else:
                    st.error("로그인 실패. 사용자명과 비밀번호를 확인해주세요.")
        else:
            username = st.text_input("새 사용자명")
            password = st.text_input("새 비밀번호", type="password")
            if st.button("회원가입"):
                if register(username, password):
                    st.success("회원가입 성공! 로그인해주세요.")
                else:
                    st.error("회원가입 실패. 다른 사용자명을 선택해주세요.")
    else:
        st.write(f"안녕하세요, {st.session_state.user}님!")

        # 데이터베이스 연결
        conn = create_connection("budget.db")
        create_table(conn)

        # 관리자 기능
        if is_admin(st.session_state.user):
            st.subheader("관리자 기능")
            user_to_grant = st.text_input("승인 권한을 부여할 사용자명")
            if st.button("승인 권한 부여"):
                if grant_approval_rights(user_to_grant):
                    st.success(f"{user_to_grant}에게 승인 권한이 부여되었습니다.")
                else:
                    st.error("승인 권한 부여에 실패했습니다.")

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

        # 대시보드 생성
        st.subheader("대시보드")
        create_dashboard(fetch_all_data(conn))

        # 로그아웃
        if st.button("로그아웃"):
            del st.session_state.user
            st.experimental_rerun()

if __name__ == "__main__":
    asyncio.run(main())