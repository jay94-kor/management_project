import streamlit as st
from database import Project, get_session

def create_dashboard():
    with get_session() as session:
        projects = session.query(Project).all()
    
    project_names = [project.name for project in projects]
    spent_budgets = [project.spent_budget for project in projects]
    assigned_budgets = [project.assigned_budget for project in projects]

    # Streamlit의 내장 파이 차트 사용
    st.pie(spent_budgets, labels=project_names)

    for project in projects:
        st.write(f"프로젝트: {project.name}")
        st.write(f"배정 예산: {project.assigned_budget}")
        st.write(f"사용 예산: {project.spent_budget}")
        st.write(f"남은 예산: {project.remaining_budget}")
        st.write("---")