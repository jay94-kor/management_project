import streamlit as st
from pages.home import home_page
from pages.project import project_page
from pages.budget import budget_page
from scripts.google_sheet import get_google_sheet
from scripts.google_drive import list_drive_files, get_file_metadata, upload_to_drive
from scripts.excel_upload import read_excel

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Project Management", "Budget Management"])

if page == "Home":
    home_page()
elif page == "Project Management":
    project_page()
elif page == "Budget Management":
    budget_page()

# Google Drive 폴더 ID (Streamlit secrets에서 가져오기)
folder_id = st.secrets["google_drive"]["folder_id"]

# Google Drive 파일 목록 가져오기
drive_files = list_drive_files(folder_id)

# 파일 카드 생성
st.write("## Project Files")
cols = st.columns(3)  # 3열로 카드 배치

for index, file in enumerate(drive_files):
    with cols[index % 3]:
        metadata = get_file_metadata(file['id'])
        st.write(f"### {metadata['title']}")
        st.write(f"Modified: {metadata['modified_date']}")
        st.write(f"Created: {metadata['created_date']}")
        if st.button(f"View {metadata['title']}", key=file['id']):
            try:
                sheet_data = get_google_sheet(file['id'])
                st.write("Project Info:")
                st.write(sheet_data["project_info"])
                st.write("Items Data:")
                st.write(sheet_data["items"])
                st.write(f"Total Budget: {sheet_data['total_budget']}")
            except Exception as e:
                st.error(f"Error occurred while fetching Google Sheet data: {e}")

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