import streamlit as st
from src.components.db import get_db_connection

def select_project():
    conn = get_db_connection()
    c = conn.cursor()
    projects = c.execute('SELECT id, name FROM projects').fetchall()
    conn.close()

    if not projects:
        st.warning("프로젝트가 없습니다. 먼저 프로젝트를 생성해주세요.")
        return None, None

    project_options = {project[1]: project[0] for project in projects}
    project_name = st.selectbox('프로젝트 선택', list(project_options.keys()))
    project_id = project_options[project_name]

    return project_id, project_name