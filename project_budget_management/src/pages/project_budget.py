import streamlit as st
from ..components.db import get_db_connection, get_projects, get_budget_items
from datetime import datetime

def show():
    st.title("프로젝트 예산 관리")

    projects = get_projects()
    project_options = {project["name"]: project["id"] for project in projects}
    project_name = st.selectbox('프로젝트 선택', list(project_options.keys()))
    project_id = project_options[project_name]

    budget_items = get_budget_items(project_id)
    budget_item_options = {item["item"]: item["id"] for item in budget_items}
    budget_item_name = st.selectbox('예산 항목 선택', list(budget_item_options.keys()))
    budget_item_id = budget_item_options[budget_item_name]

    conn = get_db_connection()
    c = conn.cursor()
    allocated_budget = c.execute('SELECT allocated_budget FROM budget_items WHERE id = ?', (budget_item_id,)).fetchone()[0]
    st.write(f"배정된 예산: {allocated_budget}")

    limit = st.number_input('예산 한도 설정', min_value=0.0, value=allocated_budget)

    if st.button('한도 저장'):
        c.execute('UPDATE budget_items SET allocated_budget = ? WHERE id = ?', (limit, budget_item_id))
        conn.commit()
        st.success('예산 한도가 저장되었습니다.')

    st.subheader('지출 내역 입력')
    description = st.text_input('지출 설명')
    amount = st.number_input('지출 금액', min_value=0.0)

    if st.button('지출 내역 저장'):
        if not description or amount <= 0:
            st.error('지출 설명과 금액을 올바르게 입력해주세요.')
        else:
            remaining_budget = c.execute('SELECT allocated_budget - COALESCE(SUM(amount), 0) FROM budget_items WHERE project_id = ?', (project_id,)).fetchone()[0]
            if amount > remaining_budget:
                st.error('예산 한도를 초과했습니다!')
            else:
                c.execute('INSERT INTO logs (user_id, project_id, action, amount, timestamp) VALUES (?, ?, ?, ?, ?)', 
                          (1, project_id, description, amount, datetime.now()))
                conn.commit()
                st.success('지출 내역이 저장되었습니다.')

    conn.close()
