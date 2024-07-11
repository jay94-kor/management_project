import streamlit as st
from app.db import create_connection
from app.dashboard import show_dashboard
from app.google_sheets import upload_data
from app.utils import get_logs

def login():
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "admin" and password == "password":  # 간단한 인증 로직
            st.session_state['logged_in'] = True
        else:
            st.error("Incorrect username or password")

def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        login()
    else:
        st.title("프로젝트 예산 관리 시스템")
        st.sidebar.title("Navigation")
        options = st.sidebar.radio("Go to", ["Dashboard", "Upload Data", "Manage Budget", "Logs"])

        if options == "Dashboard":
            show_dashboard()
        elif options == "Upload Data":
            upload_data()
        elif options == "Manage Budget":
            st.write("예산 관리 기능")
        elif options == "Logs":
            conn = create_connection("project_budget_management.db")
            logs = get_logs(conn)
            st.dataframe(logs)

if __name__ == '__main__':
    main()