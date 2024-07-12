import streamlit as st
import pandas as pd
from project_budget_management.src.components.db import get_projects

def show():
    st.title("프로젝트 목록")

    projects = get_projects()

    project_data = []
    for project in projects:
        project_data.append({
            "프로젝트명": project["name"],
            "클라이언트": project["client"],
            "작성자": project["created_by"],
            "작성일": project["created_at"],
            "행사 장소": project["event_location"],
            "최종 작성일": project["final_edit_date"],
            "행사 시작일": project["start_date"],
            "행사 종료일": project["end_date"]
        })

    df = pd.DataFrame(project_data)
    st.dataframe(df)