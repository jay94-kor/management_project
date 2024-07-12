import streamlit as st
from ..components.db import get_project_names, delete_project

def project_list_page():
    st.title("프로젝트 리스트")

    project_names = get_project_names()
    if not project_names:
        st.warning("프로젝트가 없습니다. 새 프로젝트를 추가하세요.")
    else:
        for project in project_names:
            col1, col2, col3 = st.columns([6, 1, 1])
            col1.write(project)
            if col2.button("수정", key=f"edit_{project}"):
                st.session_state['edit_project'] = project
                st.experimental_rerun()
            if col3.button("삭제", key=f"delete_{project}"):
                delete_project(project)
                st.experimental_rerun()

    if st.button("프로젝트 추가하기"):
        st.session_state['add_project'] = True
        st.experimental_rerun()