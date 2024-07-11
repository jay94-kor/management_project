import streamlit as st
import matplotlib.pyplot as plt
from database import Project, get_session

def create_dashboard():
    with get_session() as session:
        projects = session.query(Project).all()
    
    project_names = [project.name for project in projects]
    spent_budgets = [project.spent_budget for project in projects]
    assigned_budgets = [project.assigned_budget for project in projects]

    fig, ax = plt.subplots()
    ax.pie(spent_budgets, labels=project_names, autopct='%1.1f%%')
    ax.axis('equal')

    st.pyplot(fig)

    for project in projects:
        st.write(f"프로젝트: {project.name}")
        st.write(f"배정 예산: {project.assigned_budget}")
        st.write(f"사용 예산: {project.spent_budget}")
        st.write(f"남은 예산: {project.remaining_budget}")
        st.write("---")