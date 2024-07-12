import streamlit as st
import sqlite3

def show():
    st.title("프로젝트 간 예산 이동")

    conn = sqlite3.connect('budget_management.db')
    c = conn.cursor()

    # 프로젝트 선택
    projects = c.execute('SELECT id, name FROM projects').fetchall()
    project_options = {project[1]: project[0] for project in projects}
    from_project_name = st.selectbox('이동할 프로젝트 선택', list(project_options.keys()))
    from_project_id = project_options[from_project_name]
    to_project_name = st.selectbox('이동 받을 프로젝트 선택', list(project_options.keys()))
    to_project_id = project_options[to_project_name]

    transfer_amount = st.number_input('이동 금액', min_value=0, step=1)

    if st.button('프로젝트 간 예산 이동'):
        from_project_budget = c.execute('SELECT SUM(allocated_budget) FROM budget_items WHERE project_id = ?', (from_project_id,)).fetchone()[0]
        if transfer_amount > from_project_budget:
            st.error('이동 금액이 현재 프로젝트의 예산을 초과합니다.')
        else:
            # 이동할 프로젝트의 예산 항목 조정
            c.execute('UPDATE budget_items SET allocated_budget = allocated_budget - ? WHERE project_id = ?', (transfer_amount, from_project_id))
            # 이동 받을 프로젝트의 예산 항목 조정
            c.execute('UPDATE budget_items SET allocated_budget = allocated_budget + ? WHERE project_id = ?', (transfer_amount, to_project_id))
            conn.commit()
            st.success('프로젝트 간 예산이 이동되었습니다.')

    conn.close()