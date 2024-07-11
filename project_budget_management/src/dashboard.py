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

    # 차트를 이미지로 변환
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    chart_url = base64.b64encode(img.getvalue()).decode()

    st.image(img, caption='Project Budget Distribution')
    st.write(projects)