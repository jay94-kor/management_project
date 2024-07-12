import streamlit as st
from ..components.db import db_connection
from ..components.common import select_project

def show():
    st.title("마진율 유지")

    project_id, project_name = select_project()
    if not project_id:
        return

    margin_rate = st.number_input('마진율 (%)', min_value=0.0, max_value=100.0)
    if st.button('마진율 계산 및 유지'):
        with db_connection() as conn:
            c = conn.cursor()
            allocated_budget = c.execute('SELECT SUM(allocated_budget) FROM budget_items WHERE project_id = ?', (project_id,)).fetchone()[0]
            total_cost = allocated_budget * (1 - margin_rate / 100)
            
            c.execute('UPDATE budget_items SET unit_price = unit_price * ? WHERE project_id = ?', (1 - margin_rate / 100, project_id))
            conn.commit()
            st.success(f'프로젝트 {project_name}의 마진율이 {margin_rate}%로 유지되었습니다.')