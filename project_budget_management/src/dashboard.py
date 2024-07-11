import streamlit as st
from sqlalchemy.orm import Session
from database import Project, SessionLocal

def create_dashboard():
    st.title("Project Budget Dashboard")
    
    session = SessionLocal()
    projects = session.query(Project).all()
    session.close()
    
    if projects:
        data = {
            "Project Name": [project.name for project in projects],
            "Assigned Budget": [project.assigned_budget for project in projects],
            "Spent Budget": [project.spent_budget for project in projects],
            "Remaining Budget": [project.remaining_budget for project in projects]
        }
        
        st.table(data)
    else:
        st.write("No projects found.")