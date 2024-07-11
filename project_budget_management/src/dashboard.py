import streamlit as st
import matplotlib.pyplot as plt
import io
import base64
from sqlalchemy.orm import Session
from database import Project, SessionLocal

def create_dashboard():
    session = SessionLocal()
    projects = session.query(Project).all()
    session.close()
    
    # 차트 생성
    project_names = [project.name for project in projects]
    spent_budgets = [project.spent_budget for project in projects]
    assigned_budgets = [project.assigned_budget for project in projects]

    fig, ax = plt.subplots()
    ax.pie(spent_budgets, labels=project_names, autopct='%1.1f%%')
    ax.axis('equal')

    # 차트를 Streamlit에 표시
    st.pyplot(fig)

    # 프로젝트 정보 표시
    for project in projects:
        st.write(f"프로젝트: {project.name}")
        st.write(f"배정 예산: {project.assigned_budget}")
        st.write(f"사용 예산: {project.spent_budget}")
        st.write(f"남은 예산: {project.remaining_budget}")
        st.write("---")