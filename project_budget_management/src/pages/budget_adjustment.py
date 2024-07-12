import streamlit as st
from ..components.db import db_connection
from ..components.common import select_project

def show():
    st.title("항목별 예산 이동")

    project_id, project_name = select_project()
    if not project_id:
        return

    with db_connection() as conn:
        c = conn.cursor()

        # 예산 항목 선택
        budget_items = c.execute('SELECT id, item, allocated_budget FROM budget_items WHERE project_id = ?', (project_id,)).fetchall()
        budget_item_options = {item[1]: item[0] for item in budget_items}
        from_item_name = st.selectbox('이동할 항목 선택', list(budget_item_options.keys()))
        from_item_id = budget_item_options[from_item_name]
        to_item_name = st.selectbox('이동 받을 항목 선택', list(budget_item_options.keys()))
        to_item_id = budget_item_options[to_item_name]

        transfer_amount = st.number_input('이동 금액', min_value=0, step=1)

        if st.button('예산 이동'):
            from_item_budget = c.execute('SELECT allocated_budget FROM budget_items WHERE id = ?', (from_item_id,)).fetchone()[0]
            if transfer_amount > from_item_budget:
                st.error('이동 금액이 현재 항목의 예산을 초과합니다.')
            else:
                c.execute('UPDATE budget_items SET allocated_budget = allocated_budget - ? WHERE id = ?', (transfer_amount, from_item_id))
                c.execute('UPDATE budget_items SET allocated_budget = allocated_budget + ? WHERE id = ?', (transfer_amount, to_item_id))
                conn.commit()
                st.success('예산이 이동되었습니다.')