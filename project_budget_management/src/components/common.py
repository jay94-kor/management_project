import streamlit as st
from ..components.db import get_db_connection

def select_project(label="프로젝트 선택"):
    conn = get_db_connection()
    c = conn.cursor()
    projects = c.execute('SELECT id, name FROM projects').fetchall()
    project_options = {project[1]: project[0] for project in projects}
    project_name = st.selectbox(label, list(project_options.keys()))
    project_id = project_options[project_name]
    return project_id, project_name