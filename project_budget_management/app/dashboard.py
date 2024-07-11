import streamlit as st
import pandas as pd
from app.db import create_connection

def show_dashboard():
    st.header("Dashboard")
    conn = create_connection("project_budget_management.db")
    if conn is not None:
        projects_df = pd.read_sql_query("SELECT * FROM projects", conn)
        budget_items_df = pd.read_sql_query("SELECT * FROM budget_items", conn)
        
        st.subheader("Projects Overview")
        st.dataframe(projects_df)
        
        st.subheader("Budget Items Overview")
        st.dataframe(budget_items_df)
        
        # 추가적인 시각화 및 통계 기능 구현
        total_allocated_budget = budget_items_df['allocated_budget'].sum()
        total_actual_cost = budget_items_df['actual_cost'].sum()
        
        st.metric("Total Allocated Budget", f"${total_allocated_budget:,.2f}")
        st.metric("Total Actual Cost", f"${total_actual_cost:,.2f}")
        st.metric("Remaining Budget", f"${(total_allocated_budget - total_actual_cost):,.2f}")
    else:
        st.error("Database connection failed!")
