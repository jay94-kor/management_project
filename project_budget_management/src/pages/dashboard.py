import streamlit as st
import pandas as pd
import plotly.express as px
from project_budget_management.src.components.db import get_db_connection, get_projects

def show():
    st.title("대시보드")

    projects = get_projects()
    st.subheader("프로젝트 예산 상태 요약")

    project_data = []
    for project in projects:
        project_id = project["id"]
        conn = get_db_connection()
        c = conn.cursor()
        allocated_budget = c.execute('SELECT SUM(allocated_budget) FROM budget_items WHERE project_id = ?', (project_id,)).fetchone()[0]
        spent_budget = c.execute('SELECT SUM(amount) FROM logs WHERE project_id = ?', (project_id,)).fetchone()[0] or 0
        remaining_budget = allocated_budget - spent_budget
        total_revenue = c.execute('SELECT SUM(proposed_price) FROM budget_items WHERE project_id = ?', (project_id,)).fetchone()[0]
        margin_rate = ((total_revenue - allocated_budget) / total_revenue) * 100 if total_revenue else 0

        project_data.append({
            "프로젝트명": project["name"],
            "총 예산": allocated_budget,
            "지출된 예산": spent_budget,
            "잔여 예산": remaining_budget,
            "마진율": margin_rate
        })

        conn.close()

    df = pd.DataFrame(project_data)
    st.dataframe(df)

    fig = px.bar(df, x="프로젝트명", y=["총 예산", "지출된 예산", "잔여 예산"], title="프로젝트별 예산 상태")
    st.plotly_chart(fig)

    st.subheader("예산 초과 알림")
    over_budget_projects = [p for p in project_data if p["잔여 예산"] < 0]
    if over_budget_projects:
        for project in over_budget_projects:
            st.warning(f"프로젝트 '{project['프로젝트명']}'이(가) 예산을 초과했습니다!")
    else:
        st.success("모든 프로젝트가 예산 내에 있습니다.")