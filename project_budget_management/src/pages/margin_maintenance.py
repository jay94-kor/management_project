import streamlit as st
import sqlite3

def show():
    st.title("마진율 유지")

    conn = sqlite3.connect('budget_management.db')
    c = conn.cursor()

    # 프로젝트 선택
    projects = c.execute('SELECT id, name FROM projects').fetchall()
    project_options = {project[1]: project[0] for project in projects}
    project_name = st.selectbox('프로젝트 선택', list(project_options.keys()))
    project_id = project_options[project_name]

    # 마진율 입력 및 계산
    margin_rate = st.number_input('마진율 (%)', min_value=0.0, max_value=100.0)
    if st.button('마진율 계산 및 유지'):
        allocated_budget = c.execute('SELECT SUM(allocated_budget) FROM budget_items WHERE project_id = ?', (project_id,)).fetchone()[0]
        total_cost = allocated_budget * (1 - margin_rate / 100)
        
        c.execute('UPDATE budget_items SET unit_price = unit_price * ? WHERE project_id = ?', (1 - margin_rate / 100, project_id))
        conn.commit()
        st.success(f'프로젝트 {project_name}의 마진율이 {margin_rate}%로 유지되었습니다.')

    conn.close()
