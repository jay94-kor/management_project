import streamlit as st
from src.components.db import db_connection
from src.components.common import select_project

def show():
    st.title("프로젝트 간 예산 이동")

    from_project_id, from_project_name = select_project("이동할 프로젝트 선택")
    if not from_project_id:
        return

    to_project_id, to_project_name = select_project("이동 받을 프로젝트 선택")
    if not to_project_id:
        return

    transfer_amount = st.number_input('이동 금액', min_value=0, step=1)

    if st.button('프로젝트 간 예산 이동'):
        with db_connection() as conn:
            c = conn.cursor()
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