import streamlit as st
from src.pages.project_list import project_list_page
from src.pages.add_project import add_project_page
from src.pages.edit_project import edit_project_page
from src.pages.assign_manager import assign_manager_page
from src.components.db import initialize_db  # 이 줄을 추가합니다.

def main():
    if 'add_project' not in st.session_state:
        st.session_state['add_project'] = False
    if 'edit_project' not in st.session_state:
        st.session_state['edit_project'] = None

    initialize_db()  # 데이터베이스 초기화를 호출합니다.

    if st.session_state['add_project']:
        add_project_page()
    elif st.session_state['edit_project']:
        edit_project_page()
    else:
        project_list_page()

if __name__ == "__main__":
    main()