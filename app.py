import streamlit as st
from pages.home import home_page
from pages.project import project_page
from pages.budget import budget_page
from scripts.google_sheet import get_google_sheet
from scripts.google_drive import list_drive_files, upload_to_drive
from scripts.excel_upload import read_excel

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Project Management", "Budget Management"])

if page == "Home":
    home_page()
elif page == "Project Management":
    project_page()
elif page == "Budget Management":
    budget_page()

# Google Drive 파일 목록 가져오기
drive_files = list_drive_files()

# 파일 선택 드롭다운 만들기
selected_file = st.selectbox(
    "Select a file from Google Drive",
    options=[file['title'] for file in drive_files],
    format_func=lambda x: x
)

if selected_file:
    selected_file_id = next(file['id'] for file in drive_files if file['title'] == selected_file)
    try:
        sheet = get_google_sheet(selected_file_id)
        data = sheet.get_all_records()
        st.write("Google Sheet Data:")
        st.write(data)
    except Exception as e:
        st.error(f"Error occurred while fetching Google Sheet data: {e}")

# 구글 드라이브 파일 이름 입력 받기
file_name = st.text_input("Enter Google Drive File Name", "example.xlsx")

if file_name:
    try:
        file_id = get_file_id(file_name)
        st.success(f"File ID: {file_id}")
    except Exception as e:
        st.error(f"Error occurred while fetching Google Drive file ID: {e}")

# 엑셀 파일 업로드
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:
    try:
        project_info, items = read_excel(uploaded_file)
        st.write("Project Info:")
        st.write(project_info)
        st.write("Items Data:")
        st.write(items)
        
        # Google Drive에 파일 업로드
        file_id = upload_to_drive(uploaded_file)
        st.success(f"File uploaded to Google Drive with ID: {file_id}")
    except Exception as e:
        st.error(f"Error occurred while reading Excel file: {e}")