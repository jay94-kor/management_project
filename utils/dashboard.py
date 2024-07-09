import streamlit as st
import pandas as pd
import plotly.express as px
from database.db import get_approved_expenses

def create_budget_dashboard(project):
    st.subheader(f"{project['name']} 예산 사용 현황")
    
    categories = project['categories']
    allocated_amounts = project['allocated_amounts']
    used_amounts = [get_approved_expenses(project['id'], cat, item) for cat, item in zip(project['categories'], project['items'])]
    remaining_amounts = [alloc - used for alloc, used in zip(allocated_amounts, used_amounts)]
    
    fig = px.bar(x=categories, y=used_amounts, name='사용금액')
    fig.add_trace(px.bar(x=categories, y=remaining_amounts, name='잔액'))
    
    fig.update_layout(barmode='stack', title='카테고리별 예산 사용 현황')
    st.plotly_chart(fig)
    
    total_budget = sum(allocated_amounts)
    total_used = sum(used_amounts)
    usage_ratio = (total_used / total_budget) * 100
    
    st.write(f"전체 예산: {total_budget:,.0f}원")
    st.write(f"사용 금액: {total_used:,.0f}원")
    st.write(f"사용 비율: {usage_ratio:.2f}%")
    
    st.progress(usage_ratio / 100)

def create_projects_comparison_dashboard(projects):
    st.subheader("프로젝트 간 예산 비교")
    
    project_names = [p['name'] for p in projects]
    total_budgets = [sum(p['allocated_amounts']) for p in projects]
    used_budgets = [sum([get_approved_expenses(p['id'], cat, item) for cat, item in zip(p['categories'], p['items'])]) for p in projects]
    remaining_budgets = [total - used for total, used in zip(total_budgets, used_budgets)]
    
    fig = px.bar(x=project_names, y=used_budgets, name='사용금액')
    fig.add_trace(px.bar(x=project_names, y=remaining_budgets, name='잔액'))
    
    fig.update_layout(barmode='stack', title='프로젝트별 예산 사용 현황')
    st.plotly_chart(fig)
    
    for name, total, used in zip(project_names, total_budgets, used_budgets):
        usage_ratio = (used / total) * 100
        st.write(f"{name}: {usage_ratio:.2f}% 사용")
        st.progress(usage_ratio / 100)