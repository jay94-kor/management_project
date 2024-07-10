import streamlit as st
from pages.home import home_page
from pages.project import project_page
from pages.budget import budget_page
from scripts.google_sheet import get_google_sheet

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Project Management", "Budget Management"])

if page == "Home":
    home_page()
elif page == "Project Management":
    project_page()
elif page == "Budget Management":
    budget_page()

# 구글 시트 ID 입력 받기
sheet_id = st.text_input("Enter Google Sheet ID", "16MdrQJghAOhA4XTdDqLaHHf5IuSx5iGe")

if sheet_id:
    try:
        sheet = get_google_sheet(sheet_id)
        data = sheet.get_all_records()
        st.write("Google Sheet Data:")
        st.write(data)
    except Exception as e:
        st.error(f"Error occurred while fetching Google Sheet data: {e}")