import streamlit as st
from src.components.db import initialize_db
from src.pages.assign_manager import assign_manager_page

# 데이터베이스 초기화
initialize_db()

# 페이지 설정
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Assign Manager"])

if page == "Assign Manager":
    assign_manager_page()
